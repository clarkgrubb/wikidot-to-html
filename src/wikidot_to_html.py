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

RX_UL = re.compile(r'^(?P<indent>\s*)\*\s+(?P<content>\S.*)$')
RX_OL = re.compile(r'^(?P<indent>\s*)\#\s+(?P<content>\S.*)$')
RX_BLOCKQUOTE = re.compile(
    r'^(?P<greater_than_signs>>+)\s*(?P<content>.*)$')
RX_TABLE = re.compile(r'^(?P<indent>\s*)(?P<content>\|\|.*)$')
RX_HN = re.compile(
    r'^(?P<indent>\s*)(?P<plus_signs>\+{1,6})\s+(?P<content>\S.*)$')
RX_HR = re.compile(r'^(?P<indent>\s*)----(?P<content>)$')
RX_EMPTY = re.compile(r'^\s*$')
RX_P = re.compile(r'^(?P<content>.*)$')
RX_MARKERS = re.compile(r'(//|\*\*|\{\{|\}\}|@@)')
RX_WHITESPACE = re.compile(r'(\s+)')


def analyze_line(line):
    md = RX_UL.search(line)
    if md:
        return BLOCK_TYPE_UL, md
    md = RX_OL.search(line)
    if md:
        return BLOCK_TYPE_OL, md
    md = RX_TABLE.search(line)
    if md:
        return BLOCK_TYPE_TABLE, md
    md = RX_HN.search(line)
    if md:
        return BLOCK_TYPE_HN, md
    md = RX_HR.search(line)
    if md:
        return BLOCK_TYPE_HR, md
    md = RX_EMPTY.search(line)
    if md:
        return BLOCK_TYPE_EMPTY, md
    md = RX_P.search(line)
    if md:
        return BLOCK_TYPE_P, md

    raise Exception('unparseable line: {}'.format(line))


class Node(object):
    def __init__(self, raw_tag='', tag=''):
        self.children = []
        self.raw_tag = raw_tag
        self.tag = tag
        self.closure = False

    def set_closure(self, nd=True):
        self.closure = nd

    def closed(self):
        if type(self.closure) == bool:
            return self.closure
        else:
            return self.closure.closed()

    def __str__(self):
        if len(self.children) == 0:
            first = ''
            rest = ''
        elif len(self.children) == 1:
            if self.children[0] == ' ':
                first = ' '
                rest = ''
            else:
                first = ''
                rest = str(self.children[0])
        else:
            if self.children[0] == ' ':
                first = ' '
                rest = ''.join([str(child) for child in self.children[1:]])
            else:
                first = ''
                rest = ''.join([str(child) for child in self.children])

        if self.closed():
            if rest:
                return '{}<{}>{}</{}>'.format(first,
                                              self.tag,
                                              rest,
                                              self.tag)
            else:
                return first
        else:
            return '{}{}{}{}'.format(first, self.raw_tag, rest, '')


class Italic(Node):
    def __init__(self, raw_tag='//'):
        Node.__init__(self, raw_tag, 'em')


class Bold(Node):
    def __init__(self, raw_tag='**'):
        Node.__init__(self, raw_tag, 'strong')


class FixedWidth(Node):
    def __init__(self, raw_tag='{{'):
        Node.__init__(self, raw_tag, 'tt')

class LineBreak(Node):
    def __init__(self):
        pass

    def __str__(self):
        return '<br />\n'


LINE_BREAK = LineBreak()


def lex(text):
    words = RX_WHITESPACE.split(text)
    tokens = []
    for word in words:
        tokens.extend(RX_MARKERS.split(word))

    return [token for token in tokens if token]


class PhraseParser(object):

    def __init__(self):
        self.italic = False
        self.bold = False
        self.literal = False
        self.fixed_width = False
        self.top_node = Node()
        self.nodes = [self.top_node]

    def __str__(self):
        return str(self.top_node)

    def set_flag(self, cls, value):
        if cls == Italic:
            self.italic = value
        elif cls == Bold:
            self.bold = value
        elif cls == FixedWidth:
            self.fixed_width = value
        elif cls == Node:
            pass
        else:
            raise Exception('unknown class: {}'.format(cls))

    def remove_flag(self, cls):
        self.set_flag(cls, False)

    def add_flag(self, cls):
        self.set_flag(cls, True)

    def remove_all_nodes(self):
        removed_nodes = []
        while self.nodes:
            nd = self.nodes.pop()
            removed_nodes.append(nd)
            self.remove_flag(type(nd))

        return removed_nodes

    def restore_all_nodes(self, removed_nodes):
        self.top_node = type(removed_nodes.pop())()
        self.nodes = [self.top_node]
        self.restore_nodes(removed_nodes)

    def restore_nodes(self, removed_nodes):
        while removed_nodes:
            old_nd = removed_nodes.pop()
            new_nd = type(old_nd)('')
            old_nd.set_closure(new_nd)
            self.add_node(new_nd)

    def remove_nodes_to_class(self, cls_to_remove):
        removed_nodes = []
        while True:
            if not self.nodes:
                raise Exception('not on stack: {}'.format(cls_to_remove))
            nd = self.nodes.pop()
            removed_nodes.append(nd)
            self.remove_flag(type(nd))
            if type(nd) == cls_to_remove:
                break

        return removed_nodes

    def remove_node(self, cls_to_remove):
        removed_nodes = self.remove_nodes_to_class(cls_to_remove)
        nd = removed_nodes.pop()
        self.restore_nodes(removed_nodes)

        return nd

    def add_node(self, nd):
        self.nodes[-1].children.append(nd)
        self.nodes.append(nd)
        self.add_flag(type(nd))

    def add_text(self, s):
        self.nodes[-1].children.append(s)

    def parse(self, tokens):
        for i, token in enumerate(tokens):
            if RX_WHITESPACE.match(token):
                self.add_text(' ')
            elif token == '//':
                if self.italic:
                    if i > 0 and not RX_WHITESPACE.match(tokens[i - 1]):
                        nd = self.remove_node(Italic)
                        nd.set_closure(True)
                    else:
                        self.add_text('//')
                elif not self.italic:
                    if i < len(tokens) - 1 and \
                       not RX_WHITESPACE.match(tokens[i + 1]):
                        self.add_node(Italic())
                    else:
                        self.add_text('//')
            elif token == '**':
                if self.bold:
                    if i > 0 and not RX_WHITESPACE.match(tokens[i - 1]):
                        nd = self.remove_node(Bold)
                        nd.set_closure(True)
                    else:
                        self.add_text('**')
                elif not self.bold:
                    if i < len(tokens) - 1 and \
                       not RX_WHITESPACE.match(tokens[i + 1]):
                        self.add_node(Bold())
                    else:
                        self.add_text('**')
            elif token == '@@':
                self.add_text('@@')
            elif token == '{{':
                if not self.fixed_width:
                    if i < len(tokens) - 1 and \
                       not RX_WHITESPACE.match(tokens[i + 1]):
                        self.add_node(FixedWidth())
                    else:
                        self.add_text('{{')
            elif token == '}}':
                if self.fixed_width:
                    if i > 0 and not RX_WHITESPACE.match(tokens[i - 1]):
                        nd = self.remove_node(FixedWidth)
                        nd.set_closure(True)
                    else:
                        self.add_text('}}')
            else:
                self.add_text(cgi.escape(token))

        return self.top_node


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
            phrase.parse(lex(match.group('content')))
            output_stream.write(str(phrase.top_node))

    def write_close_tag(self, output_stream):
        output_stream.write('</{}>\n'.format(self.tag))

    def close(self, output_stream):
        phrase = PhraseParser()
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
        top_nodes = []
        for match in self.matches:
            phrase.parse(lex(match.group('content')))
            top_nodes.append(phrase.top_node)
            removed_nodes = phrase.remove_all_nodes()
            phrase.restore_all_nodes(removed_nodes)
        for top_node in top_nodes:
            output_stream.write('<li>')
            output_stream.write(str(top_node))
            output_stream.write('</li>\n')



class OrderedList(Block):
    def __init__(self, line, match):
        Block.__init__(self, line, BLOCK_TYPE_OL, match)

    def write_open_tag(self, output_stream):
        output_stream.write('<{}>\n'.format(self.tag))

    def write_content(self, phrase, output_stream):
        for match in self.matches:
            output_stream.write('<li>')
            phrase.parse(lex(match.group('content')))
            output_stream.write(str(phrase.top_node))
            removed_nodes = phrase.remove_all_nodes()
            output_stream.write('</li>\n')
            phrase.restore_all_nodes(removed_nodes)


class Empty(Block):
    def __init__(self, line, match):
        Block.__init__(self, line, BLOCK_TYPE_EMPTY, match)

    def close(self, output_stream):
        pass


class Paragraph(Block):

    def __init__(self, line, match):
        Block.__init__(self, line, BLOCK_TYPE_P, match)

    def write_content(self, parser, output_stream):
        tokens = []
        for i, match in enumerate(self.matches):
            parser.parse(lex(match.group('content')))
            if i < len(self.matches) - 1:
                parser.add_text(LINE_BREAK)
        output_stream.write(str(parser.top_node))


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
    md = RX_BLOCKQUOTE.search(line)
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
