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
This module provides tools for writing simple filters that are used by Scalpel
to define filter functions.
"""
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from pyparsing import alphanums, delimitedList, oneOf, ParserElement, pyparsing_common, quotedString, Word


class Operator(Enum):
    LT = '<', lambda a, b: a < b
    LE = '<=', lambda a, b: a <= b
    EQ = '==', lambda a, b: a == b
    NE = '!=', lambda a, b: a != b
    GE = '>=', lambda a, b: a >= b
    GT = '>', lambda a, b: a > b
    IN = 'in', lambda a, b: a in b
    NOT_IN = 'notin', lambda a, b: a not in b

    def __init__(self, symbol, function):
        self.symbol = symbol
        self.function = function

    def __call__(self, a, b):
        return self.function(a, b)

    @classmethod
    def value_of(cls, symbol):
        for operator in cls:
            if operator.symbol == symbol:
                return operator
        raise ValueError(f"Unrecognised symbol {symbol}")

    @classmethod
    def symbols(cls):
        return [o.symbol for o in cls]


class ExpressionParser:
    """
    The ExpressionParser is a singleton that wraps a ParserElement allowing
    to parse filter expressions.
    """

    # The single instance of this class.
    instance = None

    class __ExpressionParser:
        """
        The __ExpressionParser is the actual class of the singleton.
        """

        def __init__(self):
            """
            Creates a new __ExpressionParser, for which the wrapped ParserElement
            is not instantiated yet.
            """
            self._parser = None

        def __getattr__(self, attr):
            """
            Delegates the access to any attribute to the wrapped ParserElement.

            :param attr: The name of the attribute to get.

            :return: The value of the attribute to get.
            """
            if self._parser is None:
                self._parser = self._create_parser()
            return getattr(self._parser, attr)

        @staticmethod
        def _create_parser() -> ParserElement:
            """
            Creates the parser to use for parsing filter expressions.

            :return: The created parser.
            """
            # Defining what a variable is.
            main_variable = '${' + Word(alphanums + '-._ ') + '}'
            main_variable = main_variable.setResultsName('variable')
            main_variable.setParseAction(lambda toks: toks[1])
            second_variable = main_variable.copy().setResultsName('second_variable')

            # Defining what an operator is.
            operator = oneOf(' '.join(Operator.symbols()))
            operator = operator.setResultsName('operator')

            # Defining what the different possible values are.
            real = pyparsing_common.real.setResultsName('real')
            integer = pyparsing_common.integer.setResultsName('integer')
            boolean = oneOf("true false", caseless=True)
            boolean = boolean.setResultsName('boolean')
            boolean.setParseAction(lambda toks: list(map(lambda b: b == 'true', toks)))
            string = quotedString.setResultsName('string')
            string.setParseAction(lambda toks: list(map(lambda s: s[1:-1], toks)))

            # Defining what a single value is.
            single_value = real | integer | boolean | string
            single_value = single_value.setResultsName('value')

            # Defining what a list of values is.
            list_value = '[' + delimitedList(single_value) + ']'
            list_value = list_value.setResultsName('list')

            # Defining what a general value is.
            value = single_value | list_value

            # Defining what a complete expression is.
            variable_right = value + operator + main_variable
            variable_right = variable_right.setResultsName('right')
            variable_left = main_variable + operator + value
            variable_left = variable_left.setResultsName('left')
            both_variable = main_variable + operator + second_variable
            both_variable = both_variable.setResultsName('both')
            return variable_right | variable_left | both_variable | main_variable

    def __new__(cls):
        """
        Gives the single instance of ExpressionParser.
        """
        if ExpressionParser.instance is None:
            ExpressionParser.instance = ExpressionParser.__ExpressionParser()
        return ExpressionParser.instance

    def __getattr__(self, attr: str) -> Any:
        """
        Delegates the access to any attribute to the single instance of this class.

        :param attr: The name of the attribute to get.

        :return: The value of the attribute to get.
        """
        return getattr(self.instance, attr)


class AbstractExpression:
    """
    The AbstractExpression is the base class of the expressions used to
    define filter functions.
    Such a filter takes as input a piece of data and outputs a Boolean
    value.
    """

    def __call__(self, data: Any) -> bool:
        """
        Checks whether the given piece of data must be kept or filtered out.

        :param data: The piece of data to check.

        :return: Whether to keep the given piece of data.
        """
        raise NotImplementedError('Method "__call__()" is abstract!')


class ConjunctiveExpression(AbstractExpression):
    """
    The ConjunctiveExpression represents a conjunction of filters.
    """

    def __init__(self, *conjuncts: AbstractExpression) -> None:
        """
        Creates a new ConjunctiveExpression.

        :param conjuncts: The conjuncts of the expression.
        """
        self._conjuncts = conjuncts

    def __call__(self, data: Any) -> bool:
        """
        Checks whether the given piece of data must be kept or filtered out.
        The data is kept if and only if all conjuncts agree to keep the piece
        of data.

        :param data: The piece of data to check.

        :return: Whether to keep the given piece of data.
        """
        for conjunct in self._conjuncts:
            if not conjunct(data):
                return False
        return True


class DisjunctiveExpression(AbstractExpression):
    """
    The DisjunctiveExpression represents a disjunction of filters.
    """

    def __init__(self, *disjuncts: AbstractExpression) -> None:
        """
        Creates a new DisjunctiveExpression.

        :param disjuncts: The disjuncts of the expression.
        """
        self._disjuncts = disjuncts

    def __call__(self, data: Any) -> bool:
        """
        Checks whether the given piece of data must be kept or filtered out.
        The data is kept if and only if any disjunct agree to keep the piece
        of data.

        :param data: The piece of data to check.

        :return: Whether to keep the given piece of data.
        """
        for disjunct in self._disjuncts:
            if disjunct(data):
                return True
        return False


class SimpleExpression(AbstractExpression):
    """
    The SimpleExpression represent a filter checking a single condition.
    """

    def __init__(self, tokens: Dict[str, Any]) -> None:
        """
        Creates a new SimpleExpression.

        :param tokens: The tokens of which this expression is made of.
        """
        self._tokens = tokens

    def __call__(self, data: Any) -> bool:
        """
        Checks whether the given piece of data must be kept or filtered out.

        :param data: The piece of data to check.

        :return: Whether to keep the given piece of data.
        """
        # Retrieving the main variable.
        main_variable = data[self.get_main_variable()]

        # If there is no operator, the variable itself is used as the condition.
        operator = self.get_operator()
        if operator is None:
            return bool(main_variable)

        # Determining the value used in the operation.
        if 'second_variable' in self._tokens:
            value = data[self.get_second_variable()]
        else:
            value = self.get_value()

        # Determining the position of the main variable.
        if 'right' in self._tokens:
            left, right = value, main_variable
        else:
            left, right = main_variable, value

        # Computing the result of the operation.
        return operator(left, right)

    def get_main_variable(self) -> str:
        """
        Gives the main variable used in the condition.

        :return: The name of the variable.
        """
        return self._tokens['variable']

    def get_second_variable(self) -> Optional[str]:
        """
        Gives the second variable used in the condition, if any.

        :return: The name of the variable.
        """
        return self._tokens.get('second_variable')

    def get_operator(self) -> Optional[Callable[[Any, Any], bool]]:
        """
        Gives the operator used in the condition, if any.

        :return: The function corresponding to the operator.
        """
        o = self._tokens.get('operator')
        if o is None:
            return None
        return Operator.value_of(o)

    def get_value(self) -> Optional[Any]:
        """
        Gives the value used in the condition, if any.

        :return: The specified value.
        """
        list_value = self._tokens.get('list')
        if list_value is None:
            return self._tokens.get('value')
        return list_value


def _create_conjunctive_filter(expression: List[str]) -> AbstractExpression:
    """
    Creates a filter based on the evaluation of the given expressions,
    conjunctively interpreted.

    :param expression: The expression to evaluate as a filter.

    :return: The created filter.
    """
    conjuncts = []
    for conjunct in expression:
        conjuncts.append(_create_disjunctive_filter(conjunct))
    return ConjunctiveExpression(*conjuncts)


def _create_disjunctive_filter(expression: str) -> AbstractExpression:
    """
    Creates a filter based on the evaluation of the given expression,
    considered as a disjunctive expression.

    :param expression: The expression to evaluate as a filter.

    :return: The created filter.
    """
    disjuncts = []
    for disjunct in expression.split(' or '):
        disjuncts.append(_create_simple_filter(disjunct))
    return DisjunctiveExpression(*disjuncts)


def _create_simple_filter(expression: str) -> AbstractExpression:
    """
    Creates a filter based on the evaluation of the given expression,
    considered as a simple expression.

    :param expression: The expression to evaluate as a filter.

    :return: The created filter.
    """
    return SimpleExpression(ExpressionParser().parseString(expression, parseAll=True).asDict())


def create_filter(expression: Union[str, List[str]]) -> AbstractExpression:
    """
    Creates a filter based on the evaluation of the given expression.

    :param expression: The expression to evaluate as a filter.

    :return: The created filter.
    """
    try:
        if isinstance(expression, str):
            return _create_disjunctive_filter(expression)
        return _create_conjunctive_filter(expression)
    except Exception as exc:
        raise ValueError(f'Failed to parse expression "{expression}"') from exc
