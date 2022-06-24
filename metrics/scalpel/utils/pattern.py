###############################################################################
#                                                                             #
#  Scalpel - A Metrics Module                                                 #
#  Copyright (c) 2019-2021 - Univ Artois & CNRS, Exakis Nelite                #
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
#  See the GNU Lesser General Public License for more details.                #
#                                                                             #
#  You should have received a copy of the GNU Lesser General Public License   #
#  along with this program.                                                   #
#  If not, see <https://www.gnu.org/licenses/>.                               #
#                                                                             #
###############################################################################


"""
This module provides classes representing user-defined patterns, which allow
identifying and extracting data from experiment-ware output files.
"""


from enum import Enum
from re import compile, escape, sub
from typing import Callable, List, Optional, Pattern, Tuple


class NamedPattern(Enum):
    """
    The NamedPattern represents a simplified form of regular expressions,
    allowing to retrieve values for commonly used patterns.
    """

    BOOLEAN = '{boolean}', r'((?:[tT][rR][uU][eE])|(?:[fF][aA][lL][sS][eE]))'
    INTEGER = '{integer}', r'([-+]?\d+)'
    REAL = '{real}', r'([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)'
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
        Replaces this named pattern in the given string by the corresponding regular expression.
        Regular expression characters are supposed to have been previously escaped.

        :param string: The string in which to replace this named pattern.

        :return: The string in which the named pattern has been replaced (if present),
                 and a Boolean value that indicates whether a replacement has been achieved.
        """
        if self._escaped_identifier in string:
            return string.replace(self._escaped_identifier, self._regex), True
        return string, False

    @staticmethod
    def compile(string: str, exact_match: bool = False) -> Optional[Pattern]:
        """
        Compiles the given string as a regular expression using named patterns.

        :param string: The string to compile.
        :param exact_match: Whether the pattern must be matched exactly.

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

        if exact_match:
            escaped = f'^{escaped}$'

        # Compiling the pattern (if any).
        return compile(escaped) if any_found else None


class AbstractUserDefinedPattern:
    """
    The AbstractUserDefinedPattern is the parent class of the patterns specified
    by the user to retrieve data from output files of experiment-wares.
    """

    def search(self, string: str) -> Tuple[str]:
        """
        Searches the given string to retrieve the values specified by the associated pattern.

        :param string: The string to look into.

        :return: The extracted values, or an empty tuple if the pattern did not match.
        """
        raise NotImplementedError('Method "search()" is abstract!')


class NullUserDefinedPattern(AbstractUserDefinedPattern):
    """
    The NullUserDefinedPattern is a null object implementation of AbstractUserDefinedPattern,
    which never matches a given input.
    """

    def search(self, string: str) -> Tuple[str]:
        """
        Searches the given string to retrieve a value.

        :param string: The string to look into.

        :return: Always an empty tuple.
        """
        return tuple()

    def __str__(self) -> str:
        """
        Gives the string representation of this pattern.

        :return: The string representation of this pattern.
        """
        return '<no-pattern>'


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
        Searches the given string to retrieve the value specified by the associated pattern.

        :param string: The string to look into.

        :return: The extracted value, or an empty tuple if the pattern did not match.
        """
        match = self._pattern.search(string)
        if match is None:
            return tuple()
        return (match.group(self._group_id),)

    def __str__(self) -> str:
        """
        Gives the string representation of this pattern.

        :return: The string representation of this pattern.
        """
        return str(self._pattern)


class UserDefinedPatterns(AbstractUserDefinedPattern):
    """
    The UserDefinedPatterns is a composite pattern specified by the user to
    retrieve simultaneously multiple pieces of data from log files of
    experiment-wares.
    """

    def __init__(self) -> None:
        """
        Creates a new UserDefinedPatterns that initially does not match any pattern.
        """
        self._patterns: List[AbstractUserDefinedPattern] = []

    def add(self, pattern: AbstractUserDefinedPattern) -> None:
        """
        Appends a pattern to this composite pattern.

        :param pattern: The pattern to add.
        """
        self._patterns.append(pattern)

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
        for pattern in self._patterns:
            value = pattern.search(string)
            if not value:
                return tuple()
            values.extend(value)
        return tuple(values)

    def __str__(self) -> str:
        """
        Gives the string representation of this pattern.

        :return: The string representation of this pattern.
        """
        return str(self._patterns)


class LogData:
    """
    An instance of LogData contains all the information for mapping a named value
    to the pattern that defines how to extract it.
    """

    def __init__(self, names: List[str], pattern: AbstractUserDefinedPattern) -> None:
        """
        Creates a new LogData.

        :param names: The name(s) of the log data.
        :param pattern: The pattern identifying the log data.
        """
        self._names = names
        self._pattern = pattern

    def get_names(self) -> List[str]:
        """
        Gives the names of this log data.

        :return: The names of this log data.
        """
        return self._names

    def extract_value_from(self, string: str) -> Tuple[str]:
        """
        Extracts the value corresponding to this log data from the given string.

        :param string: The string to extract data from.

        :return: The value extracted from the string, or None if this log data
                 does not appear in the string.
        """
        return self._pattern.search(string)

    def __str__(self) -> str:
        """
        Gives the string representation of this log data.

        :return: The string representation of this log data.
        """
        return f'{self._names} => {self._pattern}'


def _compile_all(string: str, exact_match: bool, group_ids: Tuple[int],
                 compile_fct: Callable) -> AbstractUserDefinedPattern:
    """
    Compiles a string as a pattern allowing to identify several values.
    The values are supposed to be matched by one of the given groups.

    :param string: The string to compile as a pattern.
    :param exact_match: Whether the pattern must be matched exactly.
    :param group_ids: The indices of the groups identifying the values to retrieve.
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
        all_patterns.add(compile_fct(string, exact_match, group_id))
    return all_patterns


def compile_regex(regex: str, exact_match: bool = False,
                  group_id: int = 1) -> AbstractUserDefinedPattern:
    """
    Compiles a string as a regular expression allowing to identify a value.
    The value is supposed to be matched by the group having the given index.

    :param regex: The string to compile as a regular expression.
    :param exact_match: Whether the pattern must be matched exactly.
    :param group_id: The index of the group identifying the value to retrieve.

    :return: The compiled pattern.

    :raises ValueError: If the index of the group is incorrect given the
                        specified regular expression.
    """
    pattern = compile(f'^{regex}$') if exact_match else compile(regex)
    if group_id <= pattern.groups:
        return UserDefinedPattern(pattern, group_id)
    raise ValueError(f'"{regex}" must define {group_id} group(s) ({pattern.groups} found)')


def compile_all_regexes(regex: str, exact_match: bool = False,
                        *group_ids: int) -> AbstractUserDefinedPattern:
    """
    Compiles a string as a regular expression allowing to identify several values.
    The values are supposed to be matched by one of the given groups.

    :param regex: The string to compile as a regular expression.
    :param exact_match: Whether the pattern must be matched exactly.
    :param group_ids: The indices of the groups identifying the values to retrieve.

    :return: The compiled pattern.

    :raises ValueError: If no group index is specified or if one of the group
                        indices is incorrect given the specified regular expression.
    """
    return _compile_all(regex, exact_match, group_ids, compile_regex)


def compile_named_pattern(string: str, exact_match: bool = False,
                          pattern_id: int = 1) -> AbstractUserDefinedPattern:
    """
    Compiles a string as a simplified regular expression allowing to identify a value
    with a named pattern.
    The value is supposed to be matched by the named pattern having the given index.

    :param string: The string to compile as a simplified regular expression.
    :param exact_match: Whether the pattern must be matched exactly.
    :param pattern_id: The index of the named pattern identifying the value to retrieve.

    :return: The compiled pattern.

    :raises ValueError: If the string does not contain enough named patterns.
    """
    pattern = NamedPattern.compile(string, exact_match)
    if pattern is None:
        raise ValueError(f'"{string}" does not contain a recognized named pattern')
    if pattern_id <= pattern.groups:
        return UserDefinedPattern(pattern, pattern_id)
    raise ValueError(f'"{string}" must define {pattern_id} pattern(s) ({pattern.groups} found)')


def compile_all_named_patterns(string: str, exact_match: bool = False,
                               *pattern_ids: int) -> AbstractUserDefinedPattern:
    """
    Compiles a string as a simplified regular expression allowing to identify several values
    with named patterns.
    The values are supposed to be matched by one of the named patterns having the given indices.

    :param string: The string to compile as a simplified regular expression.
    :param exact_match: Whether the pattern must be matched exactly.
    :param pattern_ids: The indices of the named patterns identifying the values to retrieve.

    :return: The compiled pattern.

    :raises ValueError: If no group index is specified or if the string does not contain
                        enough named patterns.
    """
    return _compile_all(string, exact_match, pattern_ids, compile_named_pattern)


def compile_any(pattern: Optional[str], regex: Optional[str],
                exact: bool, *groups: int) -> AbstractUserDefinedPattern:
    """
    Compiles an AbstractUserDefinedPattern from either a simplified pattern or
    a regular expression.
    A best effort approach is attempted to deal with wrong uses of simplified
    patterns and regular expressions.

    :param pattern: The named pattern to compile (if any).
    :param regex: The regex to compile (if any).
    :param exact: Whether the pattern is exact.
    :param groups: The groups to extract with the pattern.

    :return: The compiled pattern.

    :raises ValueError: If it was not possible to compile the pattern.
    """
    if pattern is not None and regex is not None and pattern != regex:
        # Only one of pattern and regex can be specified.
        raise ValueError('Cannot compile both pattern and regex')

    # Trying to compile a named pattern.
    if pattern is not None:
        try:
            return compile_all_named_patterns(pattern, exact, *groups)
        except ValueError:
            return compile_all_regexes(pattern, exact, *groups)

    # No named pattern could be compiled: trying to compile a regular expression.
    if regex is not None:
        try:
            return compile_all_regexes(regex, exact, *groups)
        except ValueError:
            return compile_all_named_patterns(regex, exact, *groups)

    # All attempted compilations failed.
    raise ValueError(f'Failed to compile both pattern "{pattern}" and regex "{regex}"')
