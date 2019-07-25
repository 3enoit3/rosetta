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

# rosetta
def poke_column(lines, i):
    if i >= len(lines):
        return False
    line = lines[i][1].strip()
    return line.startswith("|") and line.endswith("|")

def tokenize_rosetta(lines):
    i = 0
    while i < len(lines):
        j = take_until(lines, i+1, poke_column)
        yield lines[i:j]
        i = j

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
