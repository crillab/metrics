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


class FileFormatEnum(FormatEnum):
    """
    The FileFormatEnum defines an enumeration type for representing file
    formats that are supported by Scalpel.
    """

    @classmethod
    def guess_format(cls, file: str) -> Optional[FileFormatEnum]:
        """
        Guesses the format of the given file, based on its extension.

        :param file: The name of the file to guess the format of.

        :return: The format of the file, or None if it could not be guessed.
        """
        index = file.rindex('.')
        return cls.value_of(file[index + 1:])


class CampaignFormat(FileFormatEnum):
    """
    The CampaignFormat defines the different formats that can be parsed by
    Scalpel to retrieve the data about a campaign.
    """

    CSV = 'csv'
    CSV2 = 'csv2', 'csv-2'
    TSV = 'tsv', 'table'
    REVERSE_CSV = 'reverse-csv', 'rcsv'
    REVERSE_CSV2 = 'reverse-csv2', 'reverse-csv-2', 'rcsv2', 'rcsv-2'
    REVERSE_TSV = 'reverse-tsv', 'reverse-table', 'rtsv', 'rtable'
    EVALUATION = 'evaluation', 'or'
    JSON = 'json'
    SINGLE_EXPERIMENT_LOG_FILE = 'file', 'log-file', 'one-file', 'one-log-file', 'single-file', 'single-log-file'
    MULTIPLE_EXPERIMENT_LOG_FILES = 'files', 'log-files', 'multi-files', 'multi-log-files'
    EXPERIMENT_DIRECTORY = 'dir', 'experiment-dir', 'experiment-directory', 'xp-dir', 'xp-directory'


class OutputFormat(FileFormatEnum):
    """
    The OutputFormat defines the different formats that can be parsed by
    Scalpel to retrieve the data about an experiment from the experiment-ware's
    output.
    """

    CSV = 'csv'
    CSV2 = 'csv2', 'csv-2'
    TSV = 'tsv', 'table'
    JSON = 'json'
    XML = 'xml'
    RAW_LOG = 'out', 'log'
