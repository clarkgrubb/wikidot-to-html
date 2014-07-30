#!/usr/bin/env python

import argparse
import cgi
import pprint
import re
import sys

PP = pprint.PrettyPrinter()

BLOCK_TYPE_P = 'p'
BLOCK_TYPE_UL = 'ul'
BLOCK_TYPE_OL = 'ol'
BLOCK_TYPE_BLOCKQUOTE = 'blockquote'
BLOCK_TYPE_TABLE = 'table'
BLOCK_TYPE_H1 = 'h1'
BLOCK_TYPE_H2 = 'h2'
BLOCK_TYPE_H3 = 'h3'
BLOCK_TYPE_H4 = 'h4'
BLOCK_TYPE_H5 = 'h5'
BLOCK_TYPE_H6 = 'h6'
BLOCK_TYPE_HR = 'hr'

BLOCK_TYPE_HN = '_hn'
BLOCK_TYPE_EMPTY = '_empty'

MULTILINE_BLOCK_TYPES = [BLOCK_TYPE_P,
                         BLOCK_TYPE_UL,
                         BLOCK_TYPE_OL,
                         BLOCK_TYPE_TABLE]

REGEX_UL = re.compile(r'^(?P<indent>\s*)\*\s+(?P<content>\S.*)$')
REGEX_OL = re.compile(r'^(?P<indent>\s*)\#\s+(?P<content>\S.*)$')
REGEX_BLOCKQUOTE = re.compile(
    r'^(?P<greater_than_signs>>+)\s*(?P<content>.*)$')
REGEX_TABLE = re.compile(r'^(?P<indent>\s*)(?P<content>\|\|.*)$')
REGEX_HN = re.compile(
    r'^(?P<indent>\s*)(?P<plus_signs>\+{1,6})\s+(?P<content>\S.*)$')
REGEX_HR = re.compile(r'^(?P<indent>\s*)----(?P<content>)$')
REGEX_EMPTY = re.compile(r'^\s*$')
REGEX_P = re.compile(r'^(?P<content>.*)$')
REGEX_MARKERS = re.compile(r'(//|\*\*\|\{\{|\}\}|@@)')
REGEX_WHITESPACE = re.compile(r'(\s+)')


def analyze_line(line):
    md = REGEX_UL.search(line)
    if md:
        return BLOCK_TYPE_UL, md
    md = REGEX_OL.search(line)
    if md:
        return BLOCK_TYPE_OL, md
    md = REGEX_TABLE.search(line)
    if md:
        return BLOCK_TYPE_TABLE, md
    md = REGEX_HN.search(line)
    if md:
        return BLOCK_TYPE_HN, md
    md = REGEX_HR.search(line)
    if md:
        return BLOCK_TYPE_HR, md
    md = REGEX_EMPTY.search(line)
    if md:
        return BLOCK_TYPE_EMPTY, md
    md = REGEX_P.search(line)
    if md:
        return BLOCK_TYPE_P, md

    raise Exception('unparseable line: {}'.format(line))


class Node(object):
    def __init__(self):
        self.children = []

    def __str__(self):
        return ''.join([str(child) for child in self.children])


class Italic(object):
    def __init__(self):
        self.children = []

    def __str__(self):
        s = ''.join([str(child) for child in self.children])

        return '<em>{}</em>'.format(s)


class Bold(object):
    def __init__(self):
        self.children = []

    def __str__(self):
        s = ''.join([str(child) for child in self.children])

        return '<strong>{}</strong>'.format(s)


class FixedWidth(object):
    def __init__(self):
        self.children = []

    def __str__(self):
        s = ''.join([str(child) for child in self.children])

        return '<tt>{}</tt>'.format(s)


class Phrase(object):

    def __init__(self):
        self.italic = False
        self.bold = False
        self.literal = False
        self.fixed_width = False
        self.nodes = None

    def _adjust_flags(self, cls):
        if cls == Italic:
            self.italic = False
        elif cls == Bold:
            self.bold = False
        elif cls == FixedWidth:
            self.fixed_width = False
        else:
            raise Exception('bam: {}'.format(cls))

    def _remove_node(self, cls):
        while self.nodes and type(self.nodes[-1]) != cls:
            self._adjust_flags(type(self.nodes.pop()))
        if self.nodes and type(self.nodes[-1]) == cls:
            self._adjust_flags(type(self.nodes.pop()))
        else:
            raise Exception('no node of type {} on stack'.format(cls))

    def render(self, content):
        words = REGEX_WHITESPACE.split(content)
        tokens = []
        for word in words:
            tokens.extend(REGEX_MARKERS.split(word))

        top_node = Node()
        self.nodes = [top_node]

        tokens = [token for token in tokens if token]

        for i, token in enumerate(tokens):
            if REGEX_WHITESPACE.match(token):
                self.nodes[-1].children.append(' ')
            elif token == '//':
                if self.italic:
                    if i > 0 and not REGEX_WHITESPACE.match(tokens[i - 1]):
                        self._remove_node(Italic)
                    else:
                        self.nodes[-1].children.append('//')
                elif not self.italic:
                    if i < len(tokens) - 1 and not REGEX_WHITESPACE.match(tokens[i + 1]):
                        nd = Italic()
                        self.nodes[-1].children.append(nd)
                        self.nodes.append(nd)
                        self.italic = True
                    else:
                        self.nodes[-1].children.append('//')
            elif token == '**':
                if self.bold:
                    if i > 0 and not REGEX_WHITESPACE.match(tokens[i - 1]):
                        self._remove_node(Bold)
                    else:
                        self.nodes[-1].children.append('@@')
                elif not self.bold:
                    if i < len(tokens) - 1 and not REGEX_WHITESPACE.match(tokens[i + 1]):
                        nd = Bold()
                        self.nodes[-1].children.append(nd)
                        self.nodes.append(nd)
                        self.bold = True
                    else:
                        self.nodes[-1].children.append('@@')
            elif token == '@@':
                self.nodes[-1].children.append('@@')
            elif token == '{{':
                if not self.fixed_width:
                    if i < len(tokens) - 1 and not REGEX_WHITESPACE.match(tokens[i + 1]):
                        nd = FixedWidth()
                        self.nodes[-1].children.append(nd)
                        self.nodes.append(nd)
                        self.fixed_width = True
                    else:
                        self.nodes[-1].children.append('{{')
            elif token == '}}':
                if self.fixed_width:
                    if i > 0 and not REGEX_WHITESPACE.match(tokens[i - 1]):
                        self._remove_node(FixedWidth)
                    else:
                        self.nodes[-1].children.append('}}')
            else:
                self.nodes[-1].children.append(cgi.escape(token))

        return str(top_node)


class Block(object):

    def __init__(self, line, block_type=None, match=None):
        self.lines = [line]
        if block_type:
            self.block_type = block_type
            self.matches = [match]
        else:
            self.block_type, match = analyze_line(line)
            self.matches.append(match)
        self.tag = self._tag()

    def add_line(self, line, block_type=None, match=None):
        self.lines.append(line)
        if block_type is None:
            block_type, match = analyze_line(line)
        if block_type != self.block_type:
            raise Exception('block type mismatch: {}: {}'.format(
                self.block_type, block_type))
        self.matches.append(match)

    def _tag(self):
        if self.block_type == BLOCK_TYPE_HN:
            len_plus_signs = len(self.matches[0].group('plus_signs'))
            return 'h{}'.format(len_plus_signs)

        return self.block_type

    def multiline_type(self):
        return self.block_type in MULTILINE_BLOCK_TYPES

    def write_open_tag(self, output_stream):
        output_stream.write('<{}>'.format(self.tag))

    def write_content(self, phrase, output_stream):
        for match in self.matches:
            output_stream.write(phrase.render(match.group('content')))

    def write_close_tag(self, output_stream):
        output_stream.write('</{}>\n'.format(self.tag))

    def close(self, output_stream):
        phrase = Phrase()
        self.write_open_tag(output_stream)
        self.write_content(phrase, output_stream)
        self.write_close_tag(output_stream)


class HorizontalRule(Block):
    def __init__(self, line, match):
        Block.__init__(self, line, BLOCK_TYPE_HR, match)

    def close(self, output_stream):
        output_stream.write('<hr />\n')


class UnorderedList(Block):
    def __init__(self, line, match):
        Block.__init__(self, line, BLOCK_TYPE_UL, match)

    def write_open_tag(self, output_stream):
        output_stream.write('<{}>\n'.format(self.tag))

    def write_content(self, phrase, output_stream):
        for match in self.matches:
            output_stream.write('<li>')
            output_stream.write(phrase.render(match.group('content')))
            output_stream.write('</li>\n')


class OrderedList(Block):
    def __init__(self, line, match):
        Block.__init__(self, line, BLOCK_TYPE_OL, match)

    def write_open_tag(self, output_stream):
        output_stream.write('<{}>\n'.format(self.tag))

    def write_content(self, phrase, output_stream):
        for match in self.matches:
            output_stream.write('<li>')
            output_stream.write(phrase.render(match.group('content')))
            output_stream.write('</li>\n')


class Empty(Block):
    def __init__(self, line, match):
        Block.__init__(self, line, BLOCK_TYPE_EMPTY, match)

    def close(self, output_stream):
        pass


class Paragraph(Block):

    def __init__(self, line, match):
        Block.__init__(self, line, BLOCK_TYPE_P, match)

    def write_content(self, phrase, output_stream):
        content = [phrase.render(match.group('content'))
                   for match
                   in self.matches]
        output_stream.write('<br />\n'.join(content))


def block_factory(line, block_type=None, match=None):
    if block_type == BLOCK_TYPE_UL:
        return UnorderedList(line, match)
    elif block_type == BLOCK_TYPE_OL:
        return OrderedList(line, match)
    elif block_type == BLOCK_TYPE_EMPTY:
        return Empty(line, match)
    elif block_type == BLOCK_TYPE_HR:
        return HorizontalRule(line, match)
    elif block_type == BLOCK_TYPE_P:
        return Paragraph(line, match)
    else:
        return Block(line, block_type, match)


def adjust_blockquote_level(output_stream, current_block, line, bq_level):
    md = REGEX_BLOCKQUOTE.search(line)
    if md:
        new_bq_level = len(md.group('greater_than_signs'))
        line = md.group('content')
    else:
        new_bq_level = 0

    if current_block and new_bq_level != bq_level:
        current_block.close(output_stream)
        current_block = None

    if new_bq_level > bq_level:
        for _ in range(0, new_bq_level - bq_level):
            output_stream.write('<blockquote>\n')
    elif new_bq_level < bq_level:
        for _ in range(0, bq_level - new_bq_level):
            output_stream.write('</blockquote>\n')

    return line, new_bq_level, current_block


def process_lines(input_stream, output_stream):
    current_block = None
    bq_level = 0
    for line in input_stream:
        line, bq_level, current_block = adjust_blockquote_level(output_stream,
                                                                current_block,
                                                                line,
                                                                bq_level)

        block_type, match = analyze_line(line)

        if not current_block:
            current_block = block_factory(line, block_type, match)
        elif (block_type == current_block.block_type and
              current_block.multiline_type):
            current_block.add_line(line, block_type, match)
        else:
            if current_block:
                current_block.close(output_stream)
            current_block = block_factory(line, block_type, match)

    if current_block:
        current_block.close(output_stream)

    adjust_blockquote_level(output_stream, None, '', bq_level)


def wikidot_to_html(input_stream, output_stream):
    process_lines(input_stream, output_stream)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    wikidot_to_html(sys.stdin, sys.stdout)
