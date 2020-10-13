###############################################################################
#                                                                             #
#  Scalpel - A Metrics Module                                                 #
#  Copyright (c) 2019-2020 - Univ Artois & CNRS, Exakis Nelite                #
#  -------------------------------------------------------------------------- #
#  mETRICS - rEproducible sofTware peRformance analysIs in perfeCt Simplicity #
#  sCAlPEL - extraCting dAta of exPeriments from softwarE Logs                #
#                                                                             #
#                                                                             #
#  This program is free software: you can redistribute it and/or modify it    #
#  under the terms of the GNU Lesser General Public License as published by   #
#  the Free Software Foundation, either version 3 of the License, or (at your #
#  option) any later version.                                                 #
#                                                                             #
#  This program is distributed in the hope that it will be useful, but        #
#  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY #
#  or FITNESS FOR A PARTICULAR PURPOSE.                                       #
#  See the GNU General Public License for more details.                       #
#                                                                             #
#  You should have received a copy of the GNU Lesser General Public License   #
#  along with this program.                                                   #
#  If not, see <https://www.gnu.org/licenses/>.                               #
#                                                                             #
###############################################################################


"""
Unit tests for the "pattern" module from Scalpel.
"""


from unittest import TestCase

from metrics.scalpel.config.pattern import compile_named_pattern, compile_regex


class TestCompileRegex(TestCase):
    """
    Test case for testing the compilation of regular expressions, and their
    use to extract data from a string.
    """

    def test_one_group(self) -> None:
        """
        Tests that the expected value is extracted when a regular expression
        is used, and defines only one group (the one to extract).
        """
        pattern = compile_regex(r'Here is a numbered word: ([A-Za-z]+[0-9]+)')
        self.assertEqual(('test0',), pattern.search('Here is a numbered word: test0'))
        self.assertFalse(pattern.search('Here is a numbered word: test'))
        self.assertFalse(pattern.search('Here is a numbered word: 0'))

    def test_one_group_with_non_capturing_group(self) -> None:
        """
        Tests that the expected value is extracted when a regular expression
        is used, and defines multiple groups, but only one is actually
        capturing (the one to extract).
        """
        pattern = compile_regex(r'(?:.*): ([A-Za-z]+[0-9]+)')
        self.assertEqual(('test0',), pattern.search('Here is a numbered word: test0'))
        self.assertFalse(pattern.search('Here is a numbered word: test'))
        self.assertFalse(pattern.search('Here is a numbered word: 0'))

    def test_multiple_groups(self) -> None:
        """
        Tests that the expected value is extracted when a regular expression
        is used, and defines multiple capturing groups (the one to extract
        is either the first one, or the one specified when compiling).
        """
        pattern_1 = compile_regex(r'([A-Za-z ]+): ([A-Za-z]+[0-9]+)')
        self.assertEqual(('Here is a numbered word',), pattern_1.search('Here is a numbered word: test0'))
        self.assertFalse(pattern_1.search('Here is a numbered word: test'))
        self.assertFalse(pattern_1.search('Here is a numbered word: 0'))

        pattern_2 = compile_regex(r'([A-Za-z ]+): ([A-Za-z]+[0-9]+)', group_id=2)
        self.assertEqual(('test0',), pattern_2.search('Here is a numbered word: test0'))
        self.assertFalse(pattern_2.search('Here is a numbered word: test'))
        self.assertFalse(pattern_2.search('Here is a numbered word: 0'))

    def test_error_when_not_enough_groups(self) -> None:
        """
        Tests that an exception is raised when the regular expression to compile
        does not contain enough groups w.r.t. the identifier specified for
        the group from which to get the value to extract.
        """
        self.assertRaises(ValueError, lambda: compile_regex(r'[A-Za-z ]+: [A-Za-z]+[0-9]+'))
        self.assertRaises(ValueError, lambda: compile_regex(r'(?:.*): (?:[A-Za-z]+[0-9]+)'))
        self.assertRaises(ValueError, lambda: compile_regex(r'([A-Za-z ]+): [A-Za-z]+[0-9]+', group_id=2))


class TestCompileAllRegexes(TestCase):
    """
    Test case for testing the compilation of regular expressions, and their
    use to extract several pieces of data from a string.
    """

    def test_error_when_no_group(self) -> None:
        """
        Tests that an exception is raised when no group identifiers are given
        when compiling the regular expression.
        """
        self.assertRaises(ValueError, lambda: compile_regex(r'[A-Za-z ]+: [A-Za-z]+[0-9]+'))


class TestCompileNamedPattern(TestCase):
    """
    Test case for testing the compilation of named patterns, and their use
    to extract data from a string.
    """

    def test_compile_boolean(self) -> None:
        """
        Tests that a Boolean value can be extracted from a matching string.
        """
        pattern = compile_named_pattern('Test  case for\t {boolean}.')
        self.assertIsNotNone(pattern)

        self.assertEqual(('true',), pattern.search('Test case for true.'))
        self.assertEqual(('FALSE',), pattern.search('Test   case   for   FALSE.'))
        self.assertEqual(('trUe',), pattern.search('Test\tcase\tfor\ttrUe.'))

        self.assertFalse(pattern.search(''))
        self.assertFalse(pattern.search('Test case for 1664.'))
        self.assertFalse(pattern.search('This string contains Talse.'))
        self.assertFalse(pattern.search('Test case for frRue'))

    def test_compile_integer(self) -> None:
        """
        Tests that an integer can be extracted from a matching string.
        """
        pattern = compile_named_pattern('Test  case for\t {integer}.')
        self.assertIsNotNone(pattern)

        self.assertEqual(('12',), pattern.search('Test case for 12.'))
        self.assertEqual(('-42',), pattern.search('Test   case   for   -42.'))
        self.assertEqual(('+51',), pattern.search('Test\tcase\tfor\t+51.'))

        self.assertFalse(pattern.search(''))
        self.assertFalse(pattern.search('Test case for value 1664.'))
        self.assertFalse(pattern.search('This string does not match.'))
        self.assertFalse(pattern.search('Test case for 24!'))

    def test_compile_real(self) -> None:
        """
        Tests that a real number can be extracted from a matching string.
        """
        pattern = compile_named_pattern('Test\tcase   for \t{real}.')
        self.assertIsNotNone(pattern)

        self.assertEqual(('12.',), pattern.search('Test case for 12..'))
        self.assertEqual(('+24.27',), pattern.search('Test case for +24.27.'))
        self.assertEqual(('-.42',), pattern.search('Test   case   for   -.42.'))
        self.assertEqual(('51',), pattern.search('Test\tcase\tfor\t51.'))
        self.assertEqual(('12.e16',), pattern.search('Test case for 12.e16.'))
        self.assertEqual(('+24.27E-64',), pattern.search('Test case for +24.27E-64.'))
        self.assertEqual(('-.42e+33',), pattern.search('Test   case   for   -.42e+33.'))
        self.assertEqual(('51E0',), pattern.search('Test\tcase\tfor\t51E0.'))

        self.assertFalse(pattern.search(''))
        self.assertFalse(pattern.search('Test case for +.e12.'))
        self.assertFalse(pattern.search('Test case for -.e+.'))
        self.assertFalse(pattern.search('Test case for 42E.'))
        self.assertFalse(pattern.search('This string does not match.'))
        self.assertFalse(pattern.search('Test case for +51!'))

    def test_compile_word(self) -> None:
        """
        Tests that a word can be extracted from a matching string.
        """
        pattern = compile_named_pattern('Test  case for\ta {word}.')
        self.assertIsNotNone(pattern)

        self.assertEqual(('word',), pattern.search('Test case for a word.'))
        self.assertEqual(('string',), pattern.search('Test  case  for  a  string.'))
        self.assertEqual(('sequence',), pattern.search('Test\tcase\tfor\ta\tsequence.'))

        self.assertFalse(pattern.search(''))
        self.assertFalse(pattern.search('Test case for a single word.'))
        self.assertFalse(pattern.search('This string does not match.'))
        self.assertFalse(pattern.search('Test case for a word!'))

    def test_compile_any(self) -> None:
        """
        Tests that any string can be extracted from a matching string.
        """
        pattern = compile_named_pattern('Test\tcase for  {any}  string.')
        self.assertIsNotNone(pattern)

        self.assertEqual(('',), pattern.search('Test case for  string.'))
        self.assertEqual(('a  short',), pattern.search('Test  case  for  a  short  string.'))
        self.assertEqual(('a\tquite\tlonger',), pattern.search('Test\tcase\tfor\ta\tquite\tlonger\tstring.'))

        self.assertFalse(pattern.search(''))
        self.assertFalse(pattern.search('Test case for string.'))
        self.assertFalse(pattern.search('This string does not match.'))
        self.assertFalse(pattern.search('Test case for this string!'))

    def test_escape_characters(self) -> None:
        """
        Tests that regular expression characters are escaped when using a named
        pattern.
        """
        pattern_integer = compile_named_pattern('Test+case for {integer}.')
        self.assertEqual(('42',), pattern_integer.search('Test+case for 42.'))
        self.assertFalse(pattern_integer.search('Testtttcase for 42.'))

        pattern_real = compile_named_pattern('[test] {real}.')
        self.assertEqual(('-24.27',), pattern_real.search('[test] -24.27.'))
        self.assertFalse(pattern_real.search('t -24.27.'))

        pattern_word = compile_named_pattern('Test? {word}.')
        self.assertEqual(('yes',),pattern_word.search('Test? yes.'))
        self.assertFalse(pattern_word.search('Tes no.'))

    def test_error_when_no_pattern(self) -> None:
        """
        Tests that an exception is raised when compiling a string that does not
        contain a named pattern.
        """
        self.assertRaises(ValueError, lambda: compile_named_pattern('This string has no pattern.'))
        self.assertRaises(ValueError, lambda: compile_named_pattern('There is no pattern here.'))
        self.assertRaises(ValueError, lambda: compile_named_pattern('No pattern is present in this string.'))
