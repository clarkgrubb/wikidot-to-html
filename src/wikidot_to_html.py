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

RX_UL = re.compile(
    r'^(?P<indent>\s*)(?P<raw_tag>\*)\s+(?P<content>\S.*?)(?P<br> _)?$')
RX_OL = re.compile(
    r'^(?P<indent>\s*)(?P<raw_tag>\#)\s+(?P<content>\S.*?)(?P<br> _)?$')
RX_BLOCKQUOTE = re.compile(
    r'^(?P<greater_than_signs>>+)\s*(?P<content>.*?)(?P<br> _)?$')
RX_TABLE = re.compile(
    r'^(?P<indent>\s*)(?P<content>\|\|.*?)(?P<br> _)?$')
RX_HN = re.compile(
    r'^(?P<indent>\s*)'
    r'(?P<plus_signs>\+{1,6})'
    r'\s+'
    r'(?P<content>\S.*?)'
    r'(?P<br> _)?$')
RX_HR = re.compile(r'^(?P<indent>\s*)----(?P<content>)(?P<br> _)?$')
RX_EMPTY = re.compile(r'^\s*(?P<br> _)?$')
RX_P = re.compile(r'^(?P<content>.*?)(?P<br> _)?$')
RX_MARKERS = re.compile(r'(//|\*\*|\{\{|\}\}|@@|\[!--|--\]|--|__|,,|\^\^|'
                        r'\[\[span [^\]]+\]\]|\[\[/span\]\]|\[\[/size\]\]|'
                        r'\]\]|##)')
RX_WHITESPACE = re.compile(r'(\s+)')
RX_SPAN = re.compile(r'^\[\[span ([^\]]+)\]\]$')
RX_SIZE = re.compile(r'^\[\[size ([^\]]+)\]\]$')
RX_RGB = re.compile(r'^[a-fA-F0-9]{6}$')
RX_PARSE_TRIPLE_BRACKET = re.compile(
    r'^\[\[\[(?P<href>.*)\|(?P<name>.+)\]\]\]$')
RX_PARSE_DOUBLE_BRACKET = re.compile(r'^\[\[#\s+(?P<anchor>.+)\]\]$')
RX_PARSE_SINGLE_BRACKET = re.compile(r'^\[(?P<href>\S+)\s+(?P<name>.+)\]$')
RX_TRIPLE_BRACKET = re.compile(
    r'(?P<token>^\[\[\[[^\]|]+\|[^\]|]+\]\]\])(?P<text>.*)$')
RX_DOUBLE_BRACKET = re.compile(
    r'^(?P<token>\[\[[^\]]+\]\])(?P<text>.*)$')
RX_SINGLE_BRACKET = re.compile(
    r'^(?P<token>\[[^\]]+\])(?P<text>.*)$')
RX_DOUBLED_CHAR = re.compile(r'^(//|\*\*|\{\{|\}\}|--|__|,,|\^\^|@@|@<|>@)')
RX_COMMENT = re.compile(r'^(\[!--.*?--\])(?P<text>.*)$')
RX_COLOR_HEAD = re.compile(r'^(?P<token>##[a-zA-Z0-9 ]+\|)(?P<text>.*)$')
RX_LEAD_WHITESPACE = re.compile(r'^(?P<token>\s+)(?P<text>.*)$')
RX_URL = re.compile(
    r'^(?P<token>https?://[a-zA-Z0-9-._~:/#&?=+,;]*[a-zA-Z0-9-_~/#&?=+])'
    r'(?P<text>.*)$')
RX_IMAGE = re.compile(r'^\[\[image\s+(?P<src>\S+)\s*(?P<attrs>.*)\]\]$')
RX_IMAGE_ATTR = re.compile(
    r'^\s*(?P<attr>[^ =]+)'
    r'\s*=\s*'
    r'"(?P<value>[^"]*)"'
    r'\s*(?P<rest>.*)$')
RX_SPACE = re.compile(r' ')


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


class ClosureNode(object):
    def __init__(self, is_closed):
        self.is_closed = is_closed

    def closed(self):
        return self.is_closed


OPEN_NODE = ClosureNode(False)
CLOSED_NODE = ClosureNode(True)


class Node(object):
    def __init__(self, raw_tag='', open_tag='', close_tag=None):
        self.children = []
        self.raw_tag = raw_tag
        self.open_tag = open_tag
        self.close_tag = open_tag if close_tag is None else close_tag
        self.closure = OPEN_NODE

    def set_closure(self, nd=True):
        self.closure = nd

    def closed(self):
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
                                              self.open_tag,
                                              rest,
                                              self.close_tag)
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


class StrikeThru(Node):
    def __init__(self, raw_tag='--'):
        Node.__init__(self,
                      raw_tag,
                      'span style="text-decoration: line-through;"',
                      'span')


class Underline(Node):
    def __init__(self, raw_tag='__'):
        Node.__init__(self,
                      raw_tag,
                      'span style="text-decoration: underline;"',
                      'span')


class Subscript(Node):
    def __init__(self, raw_tag=',,'):
        Node.__init__(self, raw_tag, 'sub')


class Superscript(Node):
    def __init__(self, raw_tag='^^'):
        Node.__init__(self, raw_tag, 'sup')


class Span(Node):
    def __init__(self, raw_tag, tag):
        Node.__init__(self, raw_tag, tag, 'span')


class Color(Node):
    def __init__(self, raw_tag, tag):
        Node.__init__(self, raw_tag, tag, 'span')


class Size(Node):
    def __init__(self, raw_tag, tag):
        Node.__init__(self, raw_tag, tag, 'span')


class EscapeLiteral(Node):
    def __init__(self, raw_tag, tag):
        Node.__init__(self, raw_tag, tag, 'span')

    def __str__(self):
        s = ''.join([str(child) for child in self.children])
        s = RX_SPACE.sub('&#32;', s)
        return '<{}>{}</{}>'.format(self.open_tag,
                                    s,
                                    self.close_tag)


class NoEscapeLiteral(Node):
    def __init__(self, raw_tag, tag):
        Node.__init__(self, raw_tag, tag, 'span')

    def __str__(self):
        s = ''.join([str(child) for child in self.children])
        s = RX_SPACE.sub('&#32;', s)
        return '<{}>{}</{}>'.format(self.open_tag,
                                    s,
                                    self.close_tag)


class Text(object):
    def __init__(self, raw_tag='', open_tag='', close_tag=None):
        self.raw_tag = raw_tag
        self.open_tag = open_tag
        self.close_tag = open_tag if close_tag is None else close_tag

    def __str__(self):
        return self.raw_tag


class Link(Text):
    def __init__(self, raw_tag, href, content):
        Text.__init__(self, raw_tag, 'a href="{}"'.format(href), 'a')
        self.content = content

    def __str__(self):
        return '<{}>{}</{}>'.format(self.open_tag,
                                    self.content,
                                    self.close_tag)


class Anchor(Text):
    def __init__(self, raw_tag, name):
        Text.__init__(self, raw_tag, 'a name="{}"'.format(name), 'a')

    def __str__(self):
        return '<{}></{}>'.format(self.open_tag, self.close_tag)


class Image(Text):
    ATTRS = ['title', 'width', 'height', 'style', 'class', 'size']

    def __init__(self, raw_tag, src, attrs):
        Text.__init__(self,
                      raw_tag,
                      'img')
        self.src = src
        self.attrs = attrs

    def __str__(self):
        s = '<img src="{}"'.format(self.src)
        for attr in Image.ATTRS:
            value = self.attrs.get(attr, None)
            if value:
                s += ' {}="{}"'.format(attr, value)
        value = self.attrs.get('alt', self.src)
        s += ' alt="{}"'.format(value)
        value = self.attrs.get('class', 'image')
        s += ' class="{}"'.format(value)
        s += ' />'
        link = self.attrs.get('link', None)
        if link:
            s = '<a href="{}">{}</a>'.format(link, s)

        return s


class LineBreak(Node):
    def __init__(self):
        Node.__init__(self)

    def __str__(self):
        return '<br />\n'


LINE_BREAK = LineBreak()


def lex(text):
    tokens = []
    prefix_and_text = text
    prefix = ''
    text_i = 0
    while text:
        if text.startswith('['):
            md = RX_TRIPLE_BRACKET.search(text)
            if md:
                if prefix:
                    tokens.append(prefix)
                    prefix = ''
                tokens.append(md.group('token'))
                prefix_and_text = md.group('text')
                text = prefix_and_text
                text_i = 0
                continue
            md = RX_DOUBLE_BRACKET.search(text)
            if md:
                if prefix:
                    tokens.append(prefix)
                    prefix = ''
                tokens.append(md.group('token'))
                prefix_and_text = md.group('text')
                text = prefix_and_text
                text_i = 0
                continue
            md = RX_COMMENT.search(text)
            if md:
                if prefix:
                    tokens.append(prefix)
                    prefix = ''
                prefix_and_text = md.group('text')
                text = prefix_and_text
                text_i = 0
                continue
            md = RX_SINGLE_BRACKET.search(text)
            if md:
                if prefix:
                    tokens.append(prefix)
                    prefix = ''
                tokens.append(md.group('token'))
                prefix_and_text = md.group('text')
                text = prefix_and_text
                text_i = 0
                continue
        if text.startswith('##'):
            if prefix:
                tokens.append(prefix)
            md = RX_COLOR_HEAD.search(text)
            if md:
                tokens.append(md.group('token'))
                prefix_and_text = md.group('text')
                text = prefix_and_text
                text_i = 0
                continue
            tokens.append(text[0:2])
            prefix_and_text = text[2:]
            text = prefix_and_text
            text_i = 0
            continue
        md = RX_LEAD_WHITESPACE.search(text)
        if md:
            if prefix:
                tokens.append(prefix)
                prefix = ''
            tokens.append(md.group('token'))
            prefix_and_text = md.group('text')
            text = prefix_and_text
            text_i = 0
            continue
        md = RX_DOUBLED_CHAR.search(text)
        if md:
            if prefix:
                tokens.append(prefix)
                prefix = ''
            tokens.append(text[0:2])
            prefix_and_text = text[2:]
            text = prefix_and_text
            text_i = 0
            continue
        if text.startswith('http'):
            md = RX_URL.search(text)
            if md:
                tokens.append(md.group('token'))
                prefix_and_text = md.group('text')
                text = prefix_and_text
                text_i = 0
                continue
        text_i += 1
        prefix = prefix_and_text[0:text_i]
        text = prefix_and_text[text_i:]

    if prefix:
        tokens.append(prefix)

    return tokens


class Parser(object):
    def __init__(self):
        self.italic = False
        self.bold = False
        self.escape_literal = False
        self.no_escape_literal = False
        self.fixed_width = False
        self.strike_thru = False
        self.underline = False
        self.subscript = False
        self.superscript = False
        self.comment = False
        self.span_depth = 0
        self.color = False
        self.size = False
        self.top_node = Node()
        self.nodes = [self.top_node]
        self.tokens = None

    def __str__(self):
        return str(self.top_node)

    def set_flag(self, cls, value):
        if cls == Italic:
            self.italic = value
        elif cls == Bold:
            self.bold = value
        elif cls == FixedWidth:
            self.fixed_width = value
        elif cls == StrikeThru:
            self.strike_thru = value
        elif cls == Underline:
            self.underline = value
        elif cls == Subscript:
            self.subscript = value
        elif cls == Superscript:
            self.superscript = value
        elif cls == EscapeLiteral:
            self.escape_literal = value
        elif cls == NoEscapeLiteral:
            self.no_escape_literal = value
        elif cls == Span:
            if value:
                self.span_depth += 1
            else:
                self.span_depth -= 1
            if self.span_depth < 0:
                raise Exception('negative span depth')
        elif cls == Color:
            self.color = value
        elif cls == Size:
            self.size = value
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

    def handle_token(self, i, raw_tag, inside_tag, cls):
        tokens = self.tokens
        if inside_tag:
            if i > 0 and not RX_WHITESPACE.match(tokens[i - 1]):
                nd = self.remove_node(cls)
                nd.set_closure(CLOSED_NODE)
            else:
                self.add_text(raw_tag)
        else:
            if i < len(tokens) - 1 and not RX_WHITESPACE.match(tokens[i + 1]):
                self.add_node(cls())
            else:
                self.add_text(raw_tag)

    def parse_image_attrs(self, attrs):
        d = {}
        while True:
            md = RX_IMAGE_ATTR.search(attrs)
            if md:
                d[md.group('attr')] = md.group('value')
                attrs = md.group('rest')
            else:
                break

        return d

    def parse_image(self, token):
        md = RX_IMAGE.search(token)
        if md:
            src = md.group('src')
            attrs = self.parse_image_attrs(md.group('attrs'))
            self.add_text(Image(token, src, attrs))
        else:
            self.add_text(token)

    def parse(self, tokens):
        self.tokens = tokens
        for i, token in enumerate(tokens):
            if token == '@@' and self.escape_literal:
                self.escape_literal = False
                self.remove_node(EscapeLiteral)
            elif token == '>@' and self.no_escape_literal:
                self.no_escape_literal = False
                self.remove_node(NoEscapeLiteral)
            elif self.escape_literal:
                self.add_text(cgi.escape(token))
            elif self.no_escape_literal:
                self.add_text(token)
            elif token == '@@':
                self.escape_literal = True
                self.add_node(EscapeLiteral(
                    '@@',
                    'span style="white-space: pre-wrap;"'))
            elif token == '@<':
                self.no_escape_literal = True
                self.add_node(NoEscapeLiteral(
                    '@@',
                    'span style="white-space: pre-wrap;"'))
            elif RX_WHITESPACE.match(token):
                self.add_text(' ')
            elif token.startswith('[[span'):
                md = RX_SPAN.search(token)
                if md:
                    attributes = md.groups()[0]
                    self.add_node(Span(token, 'span {}'.format(attributes)))
                else:
                    self.add_text(token)
            elif token == '[[/span]]':
                if self.span_depth > 0:
                    nd = self.remove_node(Span)
                    nd.set_closure(CLOSED_NODE)
                else:
                    self.add_text(token)
            elif token.startswith('[[size'):
                md = RX_SIZE.search(token)
                if md:
                    attributes = md.groups()[0]
                    self.add_node(
                        Size(token,
                             'span style="font-size:{};"'.format(attributes)))
                else:
                    self.add_text(token)
            elif token == '[[/size]]':
                if self.size:
                    nd = self.remove_node(Size)
                    nd.set_closure(CLOSED_NODE)
                else:
                    self.add_text(token)
            elif token.startswith('[[image'):
                self.parse_image(token)
            elif token.startswith('[[['):
                md = RX_PARSE_TRIPLE_BRACKET.search(token)
                if md:
                    self.add_text(Link(token,
                                       '/' + md.group('href'),
                                       md.group('name')))
                else:
                    self.add_text(token)
            elif token.startswith('[['):
                md = RX_PARSE_DOUBLE_BRACKET.search(token)
                if md:
                    self.add_text(Anchor(token, md.group('anchor')))
                else:
                    self.add_text(token)
            elif token.startswith('['):
                md = RX_PARSE_SINGLE_BRACKET.search(token)
                if md:
                    self.add_text(
                        Link(token, md.group('href'), md.group('name')))
                else:
                    self.add_text(token)
            elif token == '##':
                if self.color:
                    nd = self.remove_node(Color)
                    nd.set_closure(CLOSED_NODE)
                else:
                    self.add_text(token)
            elif token.startswith('##'):
                if self.color:
                    raise Exception('FIXME: nested color')
                if token.endswith('|'):
                    color = token[2:-1]
                    if RX_RGB.search(color):
                        tag = 'span style="color: #{}"'.format(color.lower())
                    else:
                        tag = 'span style="color: {}"'.format(color)
                    self.add_node(Color(token, tag))
                else:
                    self.add_text(token)
            elif token == '--':
                self.handle_token(i, '--', self.strike_thru, StrikeThru)
            elif token == '__':
                self.handle_token(i, '__', self.underline, Underline)
            elif token == '//':
                self.handle_token(i, '//', self.italic, Italic)
            elif token == '**':
                self.handle_token(i, '**', self.bold, Bold)
            elif token == ',,':
                self.handle_token(i, ',,', self.subscript, Subscript)
            elif token == '^^':
                self.handle_token(i, '^^', self.superscript, Superscript)
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
                        nd.set_closure(CLOSED_NODE)
                    else:
                        self.add_text('}}')
            elif token.startswith('http'):
                md = RX_URL.search(token)
                if md:
                    self.add_text(Link(token, token, token))
                else:
                    self.add_text(cgi.escape(token))
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
        if block_type != BLOCK_TYPE_P and block_type != self.block_type:
            raise Exception('block type mismatch: {}: {}'.format(
                self.block_type, block_type))
        self.matches.append(match)

    def _tag(self):
        return self.block_type

    def multiline_type(self):
        return self.block_type in MULTILINE_BLOCK_TYPES

    def write_open_tag(self, output_stream):
        output_stream.write('<{}>'.format(self.tag))

    def write_content(self, parser, output_stream):
        for match in self.matches:
            parser.parse(lex(match.group('content')))
            output_stream.write(str(parser.top_node))

    def write_close_tag(self, output_stream):
        output_stream.write('</{}>\n'.format(self.tag))

    def close(self, output_stream):
        parser = Parser()
        self.write_open_tag(output_stream)
        self.write_content(parser, output_stream)
        self.write_close_tag(output_stream)


class Header(Block):
    next_toc_number = 0

    def __init__(self, line, match):
        Block.__init__(self, line, BLOCK_TYPE_HN, match)
        self.toc_number = Header.next_toc_number
        Header.next_toc_number += 1

    def write_open_tag(self, output_stream):
        output_stream.write('<{} id="toc{}"><span>'.format(self.tag,
                                                           self.toc_number))

    def write_close_tag(self, output_stream):
        output_stream.write('</span></{}>\n'.format(self.tag))

    def _tag(self):
        len_plus_signs = len(self.matches[0].group('plus_signs'))
        return 'h{}'.format(len_plus_signs)


class HorizontalRule(Block):
    def __init__(self, line, match):
        Block.__init__(self, line, BLOCK_TYPE_HR, match)

    def close(self, output_stream):
        output_stream.write('<hr />\n')


class Table(Block):
    def __init__(self, line, match):
        Block.__init__(self, line, BLOCK_TYPE_TABLE, match)


class List(Block):
    def __init__(self, line, match):
        self.raw_tag = match.group('raw_tag')
        Block.__init__(self, line, self.raw_tag_to_tag(self.raw_tag), match)
        self.opened_lists = None
        self.inside_line = None

    def raw_tag_to_tag(self, raw_tag):
        if raw_tag == '*':
            return BLOCK_TYPE_UL
        elif raw_tag == '#':
            return BLOCK_TYPE_OL
        else:
            raise Exception('unrecognized raw tag {}'.format(raw_tag))

    def open_list(self, output_stream, tag, indent):
        if self.inside_line.get(indent - 1, False):
            output_stream.write('\n')
        elif indent > 0:
            self.open_line(output_stream, indent - 1)
            output_stream.write('\n')
        output_stream.write('<{}>\n'.format(tag))
        self.opened_lists.append(tag)

    def close_list(self, output_stream, indent):
        if self.inside_line.get(indent, False):
            self.close_line(output_stream, indent)
        tag = self.opened_lists.pop()
        output_stream.write('</{}>\n'.format(tag))

    def open_line(self, output_stream, indent):
        if self.inside_line.get(indent, False):
            self.close_line(output_stream, indent)
        output_stream.write('<li>')
        self.inside_line[indent] = True

    def close_line(self, output_stream, indent):
        output_stream.write('</li>\n')
        self.inside_line[indent] = False

    def write_content(self, output_stream, node):
        output_stream.write(str(node))

    def close(self, output_stream):
        parser = Parser()
        node_tag_indent = []
        triple = None
        for match in self.matches:
            if not triple:
                triple = [None,
                          self.raw_tag_to_tag(match.group('raw_tag')),
                          len(match.group('indent'))]
            content = match.group('content')
            parser.parse(lex(content))
            if match.group('br'):
                parser.add_text(LINE_BREAK)
            else:
                triple[0] = parser.top_node
                node_tag_indent.append(triple)
                triple = None
                removed_nodes = parser.remove_all_nodes()

                parser.restore_all_nodes(removed_nodes)

        last_indent = -1
        self.opened_lists = []
        self.inside_line = {}
        for node, tag, indent in node_tag_indent:
            for i in range(indent, last_indent):
                self.close_list(output_stream, i + 1)
            for i in range(last_indent, indent):
                self.open_list(output_stream, tag, i + 1)
            self.open_line(output_stream, indent)
            self.write_content(output_stream, node)
            last_indent = indent
        for i in range(-1, last_indent):
            self.close_list(output_stream, i + 1)


class Empty(Block):
    def __init__(self, line, match):
        Block.__init__(self, line, BLOCK_TYPE_EMPTY, match)

    def close(self, output_stream):
        pass


class Paragraph(Block):
    def __init__(self, line, match):
        Block.__init__(self, line, BLOCK_TYPE_P, match)

    def get_content(self, parser):
        for i, match in enumerate(self.matches):
            parser.parse(lex(match.group('content')))
            if i < len(self.matches) - 1:
                parser.add_text(LINE_BREAK)

        return parser.top_node

    def close(self, output_stream):
        parser = Parser()
        top_node = self.get_content(parser)
        content = str(top_node)
        suppress_tags = False
        if len(top_node.children) == 1:
            child_node = top_node.children[0]
            if type(child_node) == Image:
                suppress_tags = True
        if content:
            if not suppress_tags:
                self.write_open_tag(output_stream)
            output_stream.write(content)
            if not suppress_tags:
                self.write_close_tag(output_stream)
            else:
                output_stream.write('\n')


def block_factory(line, block_type=None, match=None):
    if block_type == BLOCK_TYPE_UL:
        return List(line, match)
    elif block_type == BLOCK_TYPE_OL:
        return List(line, match)
    elif block_type == BLOCK_TYPE_EMPTY:
        return Empty(line, match)
    elif block_type == BLOCK_TYPE_HR:
        return HorizontalRule(line, match)
    elif block_type == BLOCK_TYPE_P:
        return Paragraph(line, match)
    elif block_type == BLOCK_TYPE_HN:
        return Header(line, match)
    elif block_type == BLOCK_TYPE_TABLE:
        return Table(line, match)
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
    continued_line = False
    for line in input_stream:
        line, bq_level, current_block = adjust_blockquote_level(output_stream,
                                                                current_block,
                                                                line,
                                                                bq_level)

        block_type, match = analyze_line(line)

        if not current_block:
            current_block = block_factory(line, block_type, match)
        elif continued_line:
            current_block.add_line(line, block_type, match)
        elif (block_type == current_block.block_type and
              current_block.multiline_type):
            current_block.add_line(line, block_type, match)
        else:
            if current_block:
                current_block.close(output_stream)
            current_block = block_factory(line, block_type, match)

        continued_line = match.group('br')

    if current_block:
        current_block.close(output_stream)

    adjust_blockquote_level(output_stream, None, '', bq_level)


def wikidot_to_html(input_stream, output_stream):
    process_lines(input_stream, output_stream)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    wikidot_to_html(sys.stdin, sys.stdout)
