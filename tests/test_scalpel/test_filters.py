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
Unit tests for the "filters" module from Scalpel.
"""


from typing import Any, Dict
from unittest import TestCase

from metrics.scalpel.config.filters import create_filter


class AbstractTestFilter(TestCase):
    """
    The AbstractTestFilter is the base class of all test cases allowing
    to test the filters that can be specified in the configuration of
    Scalpel.
    The main purpose of this class is to provide test data for evaluating
    the filter and to check whether they are properly filtered.
    """

    def setUp(self) -> None:
        """
        Creates the data to use in the tests.
        """
        self._data_1 = {
            'cpu_time': 12.13,
            'memory': 50,
            'decision': 'SATISFIABLE',
            'success': True,
            'values': [1, 2, 3, 4]
        }
        self._data_2 = {
            'cpu_time': 24.27,
            'memory': 100,
            'decision': 'UNSATISFIABLE',
            'success': True,
            'values': [1, -2, 3, -4]
        }
        self._data_3 = {
            'cpu_time': 42.51,
            'memory': 150,
            'decision': 'SATISFIABLE',
            'success': True,
            'values': [-1, 2, -3, 4]
        }
        self._data_4 = {
            'cpu_time': 1664.,
            'memory': 100,
            'decision': 'UNKNOWN',
            'success': True,
            'values': [-1, -2, -3, -4]
        }
        self._data_5 = {
            'cpu_time': 33.33,
            'memory': 200,
            'decision': 'UNKNOWN',
            'success': False,
            'values': [1, -2, -3, 4]
        }

    def assertMatches(self, data: Dict[str, Any], dynamic_filter) -> None:
        """
        Tests whether the given data is matched by the given filter.

        :param data: The data on which to evaluate the filter.
        :param dynamic_filter: The filter under test.
        """
        self.assertTrue(dynamic_filter(data))

    def assertDoesNotMatch(self, data: Dict[str, Any], dynamic_filter) -> None:
        """
        Tests whether the given data is not matched by the given filter.

        :param data: The data on which to evaluate the filter.
        :param dynamic_filter: The filter under test.
        """
        self.assertFalse(dynamic_filter(data))


class TestSimpleExpression(AbstractTestFilter):

    def test_expression_of_boolean_variable(self):
        expression = create_filter("${success}")
        self.assertMatches(self._data_1, expression)
        self.assertMatches(self._data_2, expression)
        self.assertMatches(self._data_3, expression)
        self.assertMatches(self._data_4, expression)
        self.assertDoesNotMatch(self._data_5, expression)

        expression = create_filter("${success} == true")
        self.assertMatches(self._data_1, expression)
        self.assertMatches(self._data_2, expression)
        self.assertMatches(self._data_3, expression)
        self.assertMatches(self._data_4, expression)
        self.assertDoesNotMatch(self._data_5, expression)

        expression = create_filter("${success} != false")
        self.assertMatches(self._data_1, expression)
        self.assertMatches(self._data_2, expression)
        self.assertMatches(self._data_3, expression)
        self.assertMatches(self._data_4, expression)
        self.assertDoesNotMatch(self._data_5, expression)

    def test_expression_with_maximum_value(self):
        expression = create_filter("${cpu_time} <= 1000.0")
        self.assertMatches(self._data_1, expression)
        self.assertMatches(self._data_2, expression)
        self.assertMatches(self._data_3, expression)
        self.assertDoesNotMatch(self._data_4, expression)
        self.assertMatches(self._data_5, expression)

    def test_expression_with_minimum_value(self):
        expression = create_filter("200 > ${memory}")
        self.assertMatches(self._data_1, expression)
        self.assertMatches(self._data_2, expression)
        self.assertMatches(self._data_3, expression)
        self.assertMatches(self._data_4, expression)
        self.assertDoesNotMatch(self._data_5, expression)

    def test_expression_with_forbidden_value_and_neq(self):
        expression = create_filter("'UNKNOWN' != ${decision}")
        self.assertMatches(self._data_1, expression)
        self.assertMatches(self._data_2, expression)
        self.assertMatches(self._data_3, expression)
        self.assertDoesNotMatch(self._data_4, expression)
        self.assertDoesNotMatch(self._data_5, expression)

    def test_expression_with_allowed_values(self):
        expression = create_filter("${decision} in ['SATISFIABLE', 'UNSATISFIABLE']")
        self.assertMatches(self._data_1, expression)
        self.assertMatches(self._data_2, expression)
        self.assertMatches(self._data_3, expression)
        self.assertDoesNotMatch(self._data_4, expression)
        self.assertDoesNotMatch(self._data_5, expression)

    def test_expression_with_mandatory_value(self):
        expression = create_filter("1 in ${values}")
        self.assertMatches(self._data_1, expression)
        self.assertMatches(self._data_2, expression)
        self.assertDoesNotMatch(self._data_3, expression)
        self.assertDoesNotMatch(self._data_4, expression)
        self.assertMatches(self._data_5, expression)

    def test_expression_with_forbidden_value_and_notin(self):
        expression = create_filter("2 notin ${values}")
        self.assertDoesNotMatch(self._data_1, expression)
        self.assertMatches(self._data_2, expression)
        self.assertDoesNotMatch(self._data_3, expression)
        self.assertMatches(self._data_4, expression)
        self.assertMatches(self._data_5, expression)

    def test_expression_with_two_variables(self):
        expression = create_filter("${memory} < ${cpu_time}")
        self.assertDoesNotMatch(self._data_1, expression)
        self.assertDoesNotMatch(self._data_2, expression)
        self.assertDoesNotMatch(self._data_3, expression)
        self.assertMatches(self._data_4, expression)
        self.assertDoesNotMatch(self._data_5, expression)


class TestDisjunctiveExpression(AbstractTestFilter):

    def test_expression_with_allowed_values(self):
        expression = create_filter("${decision} == 'SATISFIABLE' or 'UNSATISFIABLE' == ${decision}")
        self.assertMatches(self._data_1, expression)
        self.assertMatches(self._data_2, expression)
        self.assertMatches(self._data_3, expression)
        self.assertDoesNotMatch(self._data_4, expression)
        self.assertDoesNotMatch(self._data_5, expression)


class TestConjunctiveExpression(AbstractTestFilter):

    def test_conjunction(self):
        expression = create_filter([
            "${success}",
            "${decision} in ['SATISFIABLE', 'UNSATISFIABLE']"
        ])
        self.assertMatches(self._data_1, expression)
        self.assertMatches(self._data_2, expression)
        self.assertMatches(self._data_3, expression)
        self.assertDoesNotMatch(self._data_4, expression)
        self.assertDoesNotMatch(self._data_5, expression)

    def test_conjunction2(self):
        expression = create_filter([
            "${success}",
            "${cpu_time} <= 1000.0",
            "${decision} in ['SATISFIABLE', 'UNSATISFIABLE']"
        ])
        self.assertMatches(self._data_1, expression)
        self.assertMatches(self._data_2, expression)
        self.assertMatches(self._data_3, expression)
        self.assertDoesNotMatch(self._data_4, expression)
        self.assertDoesNotMatch(self._data_5, expression)

    def test_conjunction3(self):
        expression = create_filter([
            "${success}",
            "${cpu_time} <= 1000.0",
            "${decision} == 'SATISFIABLE' or 'UNSATISFIABLE' == ${decision}"
        ])
        self.assertMatches(self._data_1, expression)
        self.assertMatches(self._data_2, expression)
        self.assertMatches(self._data_3, expression)
        self.assertDoesNotMatch(self._data_4, expression)
        self.assertDoesNotMatch(self._data_5, expression)

    def test_conjunction4(self):
        expression = create_filter([
            "${success}",
            "${cpu_time} <= 1000.0",
            "${decision} == 'SATISFIABLE' or 'UNSATISFIABLE' == ${decision}",
            "200 > ${memory}"
        ])
        self.assertMatches(self._data_1, expression)
        self.assertMatches(self._data_2, expression)
        self.assertMatches(self._data_3, expression)
        self.assertDoesNotMatch(self._data_4, expression)
        self.assertDoesNotMatch(self._data_5, expression)

    def test_conjunction5(self):
        expression = create_filter([
            "${success}",
            "${cpu_time} <= 1000.0",
            "${decision} == 'SATISFIABLE' or 'UNSATISFIABLE' == ${decision}",
            "200 > ${memory}",
            "1 in ${values}"
        ])
        self.assertMatches(self._data_1, expression)
        self.assertMatches(self._data_2, expression)
        self.assertDoesNotMatch(self._data_3, expression)
        self.assertDoesNotMatch(self._data_4, expression)
        self.assertDoesNotMatch(self._data_5, expression)

    def test_conjunction6(self):
        expression = create_filter([
            "${success}",
            "${cpu_time} <= 1000.0",
            "${decision} == 'SATISFIABLE' or 'UNSATISFIABLE' == ${decision}",
            "200 > ${memory}",
            "2 notin ${values}"
        ])
        self.assertDoesNotMatch(self._data_1, expression)
        self.assertMatches(self._data_2, expression)
        self.assertDoesNotMatch(self._data_3, expression)
        self.assertDoesNotMatch(self._data_4, expression)
        self.assertDoesNotMatch(self._data_5, expression)


class TestCreateFilterFailures(TestCase):

    def test_no_variable(self):
        self.assertRaises(ValueError, lambda: create_filter("success"))
        self.assertRaises(ValueError, lambda: create_filter("cpu_time <= 1000.0"))
        self.assertRaises(ValueError, lambda: create_filter("'cpu_time' <= 1000.0"))
        self.assertRaises(ValueError, lambda: create_filter("200 <= 1000.0"))

    def test_incorrect_variable_format(self):
        self.assertRaises(ValueError, lambda: create_filter("{success}"))
        self.assertRaises(ValueError, lambda: create_filter("$cpu_time <= 1000.0"))
        self.assertRaises(ValueError, lambda: create_filter("'${cpu_time' <= 1000.0"))
        self.assertRaises(ValueError, lambda: create_filter("200 <= 1000.0"))

    def test_incorrect_variable_format(self):
        self.assertRaises(ValueError, lambda: create_filter("'${cpu_time' <= 1000.0"))
