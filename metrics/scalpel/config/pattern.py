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
This module provides classes defining user-defined patterns, which allow to
identify and extract data from an experiment-ware output file.
"""


from enum import Enum
from re import compile, escape, sub
from typing import Optional, Pattern


class NamedPattern(Enum):
    """
    The NamedPattern represents a simplified form of regular expressions,
    allowing to retrieve a value of a commonly used pattern.
    """

    BOOLEAN = '{boolean}', r'(([tT][rR][uU][eE])|([fF][aA][lL][sS][eE]))'
    INTEGER = '{integer}', r'([-+]?\d+)'
    REAL = '{real}', r'([-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?)'
    WORD = '{word}', r'(\w+)'
    ANY = '{any}', r'(.*?)'

    def __init__(self, identifier: str, regex: str) -> None:
        """
        Creates a new NamedPattern.

        :param identifier: The identifier of the pattern.
        :param regex: The regular expression matching the pattern.
        """
        self._identifier = identifier
        self._escaped_identifier = escape(identifier)
        self._regex = regex

    def compile(self, string: str) -> Optional[Pattern]:
        """
        Replaces this named pattern in the given string by the corresponding
        regular expression, and compiles it.

        :param string: The string in which to replace this named pattern.

        :return: The compiled pattern, or None if this named pattern does not
                 appear in the specified string.
        """
        if self._identifier in string:
            escaped = escape(string)
            escaped = sub(r'(\\\s)+', r'\\s+', escaped)
            regex = escaped.replace(self._escaped_identifier, self._regex, 1)
            return compile(regex)
        return None


class UserDefinedPattern:
    """
    The UserDefinedPattern allows to easily extract from a string a value
    identified with a regular expression.
    """

    def __init__(self, pattern: Pattern, group_id: int = 1) -> None:
        """
        Creates a new UserDefinedPattern.

        :param pattern: The pattern identifying the value to retrieve.
        :param group_id: The index of the group identifying the value.
        """
        self._pattern = pattern
        self._group_id = group_id

    def search(self, string: str) -> Optional[str]:
        """
        Searches the given string to retrieve the value specified by the
        associated pattern.

        :param string: The string to look into.

        :return: The extracted value, if any.
        """
        match = self._pattern.search(string)
        if match is None:
            return None
        return match.group(self._group_id)


def compile_regex(regex: str, group_id: int = 1) -> UserDefinedPattern:
    """
    Compiles a string as a regular expression allowing to identify a value.
    The value is supposed to be matched by the group having the given index.

    :param regex: The string to compile as a regular expression.
    :param group_id: The index of the group identifying the value to retrieve.

    :return: The compiled pattern.

    :raises: A ValueError is raised if the index of the group is incorrect
             given the specified regular expression.
    """
    pattern = compile(regex)
    if group_id <= pattern.groups:
        return UserDefinedPattern(pattern, group_id)
    raise ValueError(f'"{regex}" must define at least {group_id} group(s) ({pattern.groups} found)')


def compile_named_pattern(string: str) -> UserDefinedPattern:
    """
    Compiles a string as a simplified regular expression allowing to identify a
    value with a named pattern.

    :param string: The string to compile as a simplified regular expression.

    :return: The compiled pattern.

    :raises: A ValueError is raised if the string does not contain a
             named pattern.
    """
    for named_pattern in NamedPattern:
        pattern = named_pattern.compile(string)
        if pattern is not None:
            return UserDefinedPattern(pattern)
    raise ValueError(f'"{string}" does not contain a recognized named pattern')
