#!/usr/bin/env python

import argparse
import re
import sys

BLOCK_TYPE_P = 'p'
BLOCK_TYPE_UL = 'ul'
BLOCK_TYPE_OL = 'ol'
BLOCK_TYPE_TABLE = 'table'
BLOCK_TYPE_HN = 'hn'
BLOCK_TYPE_H1 = 'h1'
BLOCK_TYPE_H2 = 'h2'
BLOCK_TYPE_H3 = 'h3'
BLOCK_TYPE_H4 = 'h4'
BLOCK_TYPE_H5 = 'h5'
BLOCK_TYPE_H6 = 'h6'
BLOCK_TYPE_HR = 'hr'
BLOCK_TYPE_EMPTY = 'empty'

MULTILINE_BLOCK_TYPES = [BLOCK_TYPE_P,
                         BLOCK_TYPE_UL,
                         BLOCK_TYPE_OL,
                         BLOCK_TYPE_TABLE]

REGEX_UL = re.compile(r'^(?P<indent>\s*)\*\s+(?P<content>\S.*)$')
REGEX_OL = re.compile(r'^(?P<indent>\s*)\#\s+(?P<content>\S.*)$')
REGEX_TABLE = re.compile(r'^(?P<indent>\s*)(?P<content>\|\|.*)$')
REGEX_HN = re.compile(
    r'^(?P<indent>\s*)(?P<plus_signs>\+{1,6})\s+(?P<content>\S.*)$')
REGEX_HR = re.compile(r'^(?P<indent>\s*)----(?P<content>)$')
REGEX_EMPTY = re.compile(r'^\s*$')
REGEX_P = re.compile(r'^(?P<content>.*)$')


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

    def write_content(self, output_stream):
        for match in self.matches:
            output_stream.write(match.group('content'))

    def write_close_tag(self, output_stream):
        output_stream.write('</{}>\n'.format(self.tag))

    def close(self, output_stream):
        self.write_open_tag(output_stream)
        self.write_content(output_stream)
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

    def write_content(self, output_stream):
        for match in self.matches:
            output_stream.write('<li>')
            output_stream.write(match.group('content'))
            output_stream.write('</li>\n')


class OrderedList(Block):
    def __init__(self, line, match):
        Block.__init__(self, line, BLOCK_TYPE_OL, match)

    def write_open_tag(self, output_stream):
        output_stream.write('<{}>\n'.format(self.tag))

    def write_content(self, output_stream):
        for match in self.matches:
            output_stream.write('<li>')
            output_stream.write(match.group('content'))
            output_stream.write('</li>\n')


class Empty(Block):
    def __init__(self, line, match):
        Block.__init__(self, line, BLOCK_TYPE_EMPTY, match)

    def close(self, output_stream):
        pass


class Paragraph(Block):

    def __init__(self, line, match):
        Block.__init__(self, line, BLOCK_TYPE_P, match)

    def write_content(self, output_stream):
        content = [match.group('content') for match in self.matches]
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


def process_lines(input_stream, output_stream):
    current_block = None
    for line in input_stream:
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


def hyperwiki_to_html(input_stream, output_stream):
    process_lines(input_stream, output_stream)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    hyperwiki_to_html(sys.stdin, sys.stdout)
