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
This module provides the enumerations representing the formats recognized by
Scalpel.
"""


from __future__ import annotations

from enum import Enum
from typing import Optional


class FormatEnum(Enum):
    """
    The FormatEnum defines an enumeration type for representing formats
    that are considered by Scalpel to decide how to parse its inputs.
    """

    def __init__(self, *names: str) -> None:
        """
        Creates a new FormatEnum.

        :param names: The names identifying the format.
        """
        self._names = names

    def __contains__(self, identifier: str) -> bool:
        """
        Checks whether the given identifier identifies this format.
        The comparison is case insensitive.

        :param identifier: The identifier to check.

        :return: Whether this format is identified by the identifier.
        """
        for name in self._names:
            if name.lower() == identifier.lower():
                return True
        return False

    @classmethod
    def value_of(cls, identifier: str) -> Optional[FormatEnum]:
        """
        Gives the format identified by the given identifier.

        :param identifier: The identifier of the format to get.

        :return: The format identified by the given identifier, or None if
                 there is no such format.
        """
        for fmt in cls:
            if identifier in fmt:
                return fmt
        return None


class InputSetFormat(FormatEnum):
    """
    The InputSetFormat defines the different formats that can be used to
    describe the input set considered in the campaign that Scalpel is parsing.
    """

    LIST = 'list'
    FILE_LIST = 'file-list'
    FILE = 'file'
    HIERARCHY = 'hierarchy'


class CampaignFormat(FormatEnum):
    """
    The CampaignFormat defines the different formats that can be parsed by
    Scalpel to retrieve the data about a campaign.
    """

    CSV = 'csv'
    CSV2 = 'csv2', 'csv-2'
    TSV = 'tsv', 'table'
    EVALUATION = 'evaluation', 'or'
    JSON = 'json'
    RAW_LOG = 'raw', 'raw-log'
    FLAT_LOG_DIRECTORY = 'flat-dir'
    FLAT_LOG_DIRECTORY_MULTIPLE_FILES = 'flat-dir-mult', 'flat-dir-multi', 'flat-dir-multiple-files'
    DEEP_LOG_DIRECTORY = 'deep-dir'


class OutputFormat(FormatEnum):
    """
    The OutputFormat defines the different formats that can be parsed by
    Scalpel to retrieve the data about an experiment from the experiment-ware's
    output.
    """

    CSV = 'csv'
    CSV2 = 'csv2', 'csv-2'
    TSV = 'tsv', 'table'
    JSON = 'json'
    RAW_LOG = 'out', 'log'
