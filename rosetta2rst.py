#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Produce a valid rst"""

import sys
import argparse
import unittest
import logging

# rst
def poke_header(lines, i):
    return i <= len(lines) - 3 and lines[i][1].strip() == "" and lines[i+1][1].startswith(".. rosetta::") and lines[i+2][1].strip() == ""

def poke_footer(lines, i):
    return i <= len(lines) - 2 and lines[i][1].strip() == "" and not lines[i+1][1].startswith("\t")

def take_until(lines, i, predicate):
    while i < len(lines) and not predicate(lines, i):
        i += 1
    return i

def tokenize_rst(lines):
    i = 0
    while i < len(lines):
        if poke_header(lines, i):
            j = take_until(lines, i + 3, poke_footer)
            yield lines[i:j+1]
            i = j + 1
        else:
            j = take_until(lines, i, poke_header)
            yield lines[i:j]
            i = j

def is_rosetta(token):
    return poke_header(token, 0)

# rosetta
def poke_column(lines, i):
    if i >= len(lines):
        return False
    line = lines[i][1].strip()
    return line.startswith("|") and line.count("|") >= 2

def poke_row(lines, i):
    if i >= len(lines):
        return False
    line = lines[i][1].strip()
    return line == "--"

def poke_delim(lines, i):
    return poke_column(lines, i) or poke_row(lines, i)

def tokenize_rosetta(lines):
    i = 0
    while i < len(lines):
        j = take_until(lines, i+1, poke_delim)
        yield lines[i:j]
        i = j

def is_column(token):
    return poke_column(token, 0)

def is_row(token):
    return poke_row(token, 0)

def split_column(token):
    if not is_column(token):
        return None
    header_fields = token[0][1].strip().split("|")
    if len(header_fields) < 2:
        return None
    lang = header_fields[1].strip()
    code = [(token[0][0], header_fields[2])] + token[1:]
    return lang, code

# html
def generate_html_code(lines):
    return "<br>".join(lines)

def generate_html_row(cols, sep="td"):
    row = "\n".join(["    <{0}>{1}</{0}>".format(sep,col) for col in cols])
    return "  <tr>\n" + row + "\n  </tr>"

def generate_html_table(headers, rows):
    body = "\n".join(rows)
    return "<table>\n"+ headers + "\n" + body + "\n</table>"

# logic
def generate_block(block):
    tokens = tokenize_rosetta(block)
    for token in token:
        pass

def generate(rst):
    return """
P1

.. raw:: html

    <table>
        <tr>
            <th>type</th>
            <th>c++</th>
            <th>js</th>
        </tr>
        <tr>
            <td>declaration</td>
            <td>int i = 0;</td>
            <td>var i = 0;</td>
        </tr>
        <tr>
            <td>comparision</td>
            <td>a==b</td>
            <td>a===b</td>
        </tr>
    </table

P2
"""
    out = []
    lines = enumerate(rst.splitlines())
    blocks = tokenize_rst(lines)
    for block in blocks:
        is_rosetta = poke_header(block, 0)
        if is_rosetta:
            out += generate_block(block)
        else:
            out += block

def main():
    """Entry point"""

    # Parse options
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true", default=False,
                        help="show debug information")
    args = parser.parse_args()

    # Configure debug
    if args.debug:
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        logging.debug("Enabled debug logging")

    return 0

if __name__ == "__main__":
    sys.exit(main())


class Tests(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    """Unit tests"""
    # run test suite with
    # python -m unittest <this_module_name_without_py_extension>

    def setUp(self):
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    # Helpers
    def enumerate(self, lst, start=0):
        return list(enumerate(lst, start))

    def flat_enumerate(self, lst, start=0):
        i = start
        for sub_lst in lst:
            yield self.enumerate(sub_lst, i)
            i += len(sub_lst)

    def assertEqualGenerators(self, lhs, rhs):
        self.assertEqual(list(lhs), list(rhs))

    def test_rst(self):
        rst = self.enumerate(["P1","",".. rosetta::","","\t|c++|","\tint i;","","P2"])
        ref_tokens = self.flat_enumerate([["P1"], ["",".. rosetta::","","\t|c++|","\tint i;",""], ["P2"]])
        tokens = tokenize_rst(rst)
        self.assertEqualGenerators(ref_tokens, tokens)

    def test_rosetta(self):
        block = self.enumerate(["",".. rosetta::","","\t|c++|","\tint i;","\t|js|","var i"])
        ref_tokens = self.flat_enumerate([["",".. rosetta::",""], ["\t|c++|","\tint i;"], ["\t|js|","var i"]])
        tokens = tokenize_rosetta(block)
        self.assertEqualGenerators(ref_tokens, tokens)

        self.assertEqual(split_column(self.enumerate(["\t|c++|\tint i;"])), ("c++", [(0,"\tint i;")]))
        self.assertEqual(split_column(self.enumerate(["    |   c++   |   int i;"])), ("c++", [(0,"   int i;")]))
        self.assertEqual(split_column(self.enumerate(["\tc++   |","\tint i;"])), None)
        self.assertEqual(split_column(self.enumerate(["\t|c++","\tint i;"])), None)

    def test_html(self):
        self.assertEqual(generate_html_code(["int"]), "int")
        self.assertEqual(generate_html_code(["int","i"]), "int<br>i")
        rows = ["declaration", "int i = 0;", "var i = 0;"]
        self.assertEqual(generate_html_row(rows), "  <tr>\n    <td>declaration</td>\n    <td>int i = 0;</td>\n    <td>var i = 0;</td>\n  </tr>")
        headers = ["", "c++", "js"]

    def test_generate(self):
        rst = """
P1

.. rosetta::

    |type|declaration
    |c++|int i = 0;
    |js|var i = 0;
    --
    |type|comparision
    |c++|a==b
    |js|a===b

P2
"""
        ref = """
P1

.. raw:: html

    <table>
        <tr>
            <th>type</th>
            <th>c++</th>
            <th>js</th>
        </tr>
        <tr>
            <td>declaration</td>
            <td>int i = 0;</td>
            <td>var i = 0;</td>
        </tr>
        <tr>
            <td>comparision</td>
            <td>a==b</td>
            <td>a===b</td>
        </tr>
    </table

P2
"""
        out = generate(rst)
        self.assertEqual(ref, out)
