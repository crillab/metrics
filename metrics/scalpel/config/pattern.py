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
identify and extract data from experiment-ware output files.
"""


from enum import Enum
from re import compile, escape, sub
from typing import List, Optional, Pattern, Tuple, Callable


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

    def _replace_in(self, string: str) -> Tuple[str, bool]:
        """
        Replaces this named pattern in the given string by the corresponding
        regular expression.

        :param string: The string in which to replace this named pattern.

        :return: The string in which the named pattern has been replaced (if
                 present), and a Boolean value that indicates whether a
                 replacement has been achieved.
        """
        if self._escaped_identifier in string:
            return string.replace(self._escaped_identifier, self._regex), True
        return string, False

    @staticmethod
    def compile(string: str, exact: bool = False) -> Optional[Pattern]:
        """
        Compiles the given string as a regular expression using named patterns.

        :param string: The string to compile.

        :return: The compiled pattern, or None if the input string does not
                 contain any named pattern.
        """
        # Escaping "classical" regular expression characters.
        escaped = escape(string)
        escaped = sub(r'(\\\s)+', r'\\s+', escaped)

        # Replacing each named pattern.
        any_found = False
        for named_pattern in NamedPattern:
            escaped, found = named_pattern._replace_in(escaped)
            any_found = any_found or found

        if exact:
            escaped = f'^{escaped}$'

        # Compiling the pattern (if any).
        return compile(escaped) if any_found else None


class AbstractUserDefinedPattern:
    """
    The AbstractUserDefinedPattern is the parent class of the patterns
    specified by the user to retrieve data from output files of
    experiment-wares.
    """

    def search(self, string: str) -> Tuple[str]:
        """
        Searches the given string to retrieve the values specified by the
        associated pattern.

        :param string: The string to look into.

        :return: The extracted values, or an empty tuple if the pattern did
                 not match.
        """
        raise NotImplementedError('Method "search()" is abstract!')


class NullUserDefinedPattern(AbstractUserDefinedPattern):
    """
    The NullUserDefinedPattern is a null object implementation of
    AbstractUserDefinedPattern, which never matches a given input.
    """

    def search(self, string: str) -> Tuple[str]:
        """
        Searches the given string to retrieve a value.

        :param string: The string to look into.

        :return: Always an empty tuple.
        """
        return tuple()


class UserDefinedPattern(AbstractUserDefinedPattern):
    """
    The UserDefinedPattern is a pattern specified by the user to retrieve
    exactly one piece of data from log files of experiment-wares.
    """

    def __init__(self, pattern: Pattern, group_id: int = 1) -> None:
        """
        Creates a new UserDefinedPattern.

        :param pattern: The pattern identifying the value to retrieve.
        :param group_id: The index of the group identifying the value.
        """
        self._pattern = pattern
        self._group_id = group_id

    def search(self, string: str) -> Tuple[str]:
        """
        Searches the given string to retrieve the value specified by the
        associated pattern.

        :param string: The string to look into.

        :return: The extracted value, or an empty tuple if the pattern did
                 not match.
        """
        match = self._pattern.search(string)
        if match is None:
            return tuple()
        return match.group(self._group_id),


class UserDefinedPatterns(AbstractUserDefinedPattern):
    """
    The UserDefinedPatterns is a composite pattern specified by the user to
    retrieve simultaneously multiple pieces of data from log files of
    experiment-wares.
    """

    def __init__(self) -> None:
        """
        Creates a new UserDefinedPatterns that does not have any child.
        """
        self._children: List[AbstractUserDefinedPattern] = []

    def add(self, pattern: AbstractUserDefinedPattern) -> None:
        """
        Appends a pattern to the children of this composite pattern.

        :param pattern: The pattern to add.
        """
        self._children.append(pattern)

    def search(self, string: str) -> Tuple[str]:
        """
        Searches the given string to retrieve the values specified by the
        associated patterns.

        :param string: The string to look into.

        :return: The extracted values, or an empty tuple if the pattern did not
                 match, i.e., if at least one of the patterns aggregated in
                 this composite did not match the given string.
        """
        values = []
        for child in self._children:
            value = child.search(string)
            if not value:
                return tuple()
            values.extend(value)
        return tuple(values)


def _compile_all(string: str, exact: bool, group_ids: Tuple[int],
                 compile_fct: Callable[[str, bool, int], AbstractUserDefinedPattern]) -> AbstractUserDefinedPattern:
    """
    Compiles a string as a pattern allowing to identify several values.
    The values are supposed to be matched by one of the given groups.

    :param string: The string to compile as a pattern.
    :param exact: Whether the pattern must be matched exactly.
    :param group_ids: The indices of the groups identifying the values
                      to retrieve.
    :param compile_fct: The function to use to compile the pattern.

    :return: The compiled pattern.

    :raises ValueError: If no group index is specified or if one of the group
                        indices is incorrect given the specified pattern.
    """
    # Checking that there is at least one group.
    if not group_ids:
        raise ValueError(f'Missing group indices for pattern "{string}"')

    # Aggregating the patterns.
    all_patterns = UserDefinedPatterns()
    for group_id in group_ids:
        all_patterns.add(compile_fct(string, exact, group_id))
    return all_patterns


def compile_regex(regex: str, exact: bool = False, group_id: int = 1) -> AbstractUserDefinedPattern:
    """
    Compiles a string as a regular expression allowing to identify a value.
    The value is supposed to be matched by the group having the given index.

    :param regex: The string to compile as a regular expression.
    :param exact: Whether the pattern must be matched exactly.
    :param group_id: The index of the group identifying the value to retrieve.

    :return: The compiled pattern.

    :raises ValueError: If the index of the group is incorrect given the
                        specified regular expression.
    """
    if exact:
        pattern = compile(f'^{regex}$')
    else:
        pattern = compile(regex)

    if group_id > pattern.groups:
        raise ValueError(f'"{regex}" must define at least {group_id} group(s) ({pattern.groups} found)')
    return UserDefinedPattern(pattern, group_id)


def compile_all_regexes(regex: str, exact: bool = False, *group_ids: int) -> AbstractUserDefinedPattern:
    """
    Compiles a string as a regular expression allowing to identify several
    values.
    The values are supposed to be matched by one of the given groups.

    :param regex: The string to compile as a regular expression.
    :param exact: Whether the pattern must be matched exactly.
    :param group_ids: The indices of the groups identifying the values to
                      retrieve.

    :return: The compiled pattern.

    :raises ValueError: If no group index is specified or if one of the group
                        indices is incorrect given the specified regular
                        expression.
    """
    return _compile_all(regex, exact, group_ids, compile_regex)


def compile_named_pattern(string: str, exact: bool = False, pattern_id: int = 1) -> AbstractUserDefinedPattern:
    """
    Compiles a string as a simplified regular expression allowing to
    identify a value with a named pattern.
    The value is supposed to be matched by the named pattern having the
    given index.

    :param string: The string to compile as a simplified regular expression.
    :param exact: Whether the pattern must be matched exactly.
    :param pattern_id: The index of the named pattern identifying the value to
                       retrieve.

    :return: The compiled pattern.

    :raises ValueError: If the string does not contain enough named patterns.
    """
    pattern = NamedPattern.compile(string, exact)
    if pattern is None:
        raise ValueError(f'"{string}" does not contain a recognized named pattern')
    if pattern_id > pattern.groups:
        raise ValueError(f'"{string}" must define at least {pattern_id} pattern(s) ({pattern.groups} found)')
    return UserDefinedPattern(pattern, pattern_id)


def compile_all_named_patterns(string: str, exact: bool = False, *pattern_ids: int) -> AbstractUserDefinedPattern:
    """
    Compiles a string as a simplified regular expression allowing to identify
    several values with named patterns.
    The values are supposed to be matched by one of the named patterns having
    the given indices.

    :param string: The string to compile as a simplified regular expression.
    :param exact: Whether the pattern must be matched exactly.
    :param pattern_ids: The indices of the the named patterns identifying the
                        values to retrieve.

    :return: The compiled pattern.

    :raises ValueError: If no group index is specified or if the string does
                        not contain enough named patterns.
    """
    return _compile_all(string, exact, pattern_ids, compile_named_pattern)
