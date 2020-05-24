###############################################################################
#                                                                             #
#  Core - A Metrics Module                                                    #
#  Copyright (c) 2019-2020 - Univ Artois & CNRS, Exakis Nelite                #
#  -------------------------------------------------------------------------- #
#  mETRICS - rEproducible sofTware peRformance analysIs in perfeCt Simplicity #
#  Core - Core components for Metrics                                         #
#                                                                             #
#                                                                             #
#  This program is free software: you can redistribute it and/or modify it    #
#  under the terms of the GNU Lesser General Public License as published by   #
#  the Free Software Foundation, either version 3    of the License, or (at your #
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
This module provides classes permitting to verify and parse a given value.
"""
import re
from typing import Any


class TypingStrategy:
    """
    TypingStrategy is an abstract object that permits to verify and parse a given object.
    """

    def verify(self, obj: Any) -> bool:
        """
        Verifies if it is possible to parse this object.
        @param obj: object to verify.
        @return: True if the object is parsable.
        """
        raise NotImplementedError('This abstract method needs to be implemented.')

    def parse(self, obj: Any) -> Any:
        """
        Parse the object previously verified.
        @param obj: object to parse.
        @return: Parsed object.
        """
        raise NotImplementedError('This abstract method needs to be implemented.')


class IntegerTypingStrategy(TypingStrategy):
    """
    IntegerTypingStrategy is an object that permits to verify and parse a given object.
    It must have the conformity of an integer regex.
    """

    def __init__(self):
        """
        Creates an typing strategy respecting the integer pattern.
        """
        self.pattern = re.compile(r'^[-+]?[0-9]+$')

    def verify(self, obj: Any) -> bool:
        strr = str(obj)
        return bool(self.pattern.match(strr))

    def parse(self, obj: Any) -> int:
        return int(str(obj))


class FloatTypingStrategy(TypingStrategy):
    """
    FloatTypingStrategy is an object that permits to verify and parse a given object.
    It must have the conformity of a float regex.
    """

    def __init__(self):
        """
        Creates an typing strategy respecting the float pattern.
        """
        self.pattern = re.compile(r'^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$')

    def verify(self, obj: Any) -> bool:
        strr = str(obj)
        return bool(self.pattern.match(strr))

    def parse(self, obj: Any) -> float:
        return float(str(obj))


class StringTypingStrategy(TypingStrategy):
    """
    StringTypingStrategy is an object that permits to verify and parse a given object.
    It must be a string.
    """

    def verify(self, obj: Any) -> bool:
        return isinstance(obj, str)

    def parse(self, obj: Any) -> float:
        return obj


class AnyTypingStrategy(TypingStrategy):
    """
    AnyTypingStrategy accepts all kind of objects (also None).
    """

    def verify(self, obj: Any) -> bool:
        return True

    def parse(self, obj: Any) -> Any:
        return obj


class TypingStrategyEnum:
    """
    An enumeration of classical typing strategies.
    """
    INTEGER = IntegerTypingStrategy()
    FLOAT = FloatTypingStrategy()
    STRING = StringTypingStrategy()
    ANY = AnyTypingStrategy()
