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
This module provides the enumerations representing the formats recognized by Scalpel.
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
        The comparison is case-insensitive.

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

    @classmethod
    def all_yaml_string(cls):
        return [f._names[0] for f in cls]


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
    SINGLE_EXPERIMENT_LOG_FILE = 'file', 'log-file', 'one-file', 'single-file'
    MULTIPLE_EXPERIMENT_LOG_FILES = 'files', 'log-files', 'multi-files'
    EXPERIMENT_DIRECTORY = 'dir', 'experiment-dir', 'experiment-directory', 'xp-dir', 'xp-directory'

    def is_csv(self):
        """
        Checks whether this format identifies a variant of the CSV format.

        :return: Whether this format is a CSV format.
        """
        return self in (CampaignFormat.CSV,
                        CampaignFormat.CSV2,
                        CampaignFormat.TSV)

    def is_reverse_csv(self):
        """
        Checks whether this format identifies a variant of the reverse CSV format.

        :return: Whether this format is a reverse CSV format.
        """
        return self in (CampaignFormat.REVERSE_CSV,
                        CampaignFormat.REVERSE_CSV2,
                        CampaignFormat.REVERSE_TSV)


class OutputFormat(FileFormatEnum):
    """
    The OutputFormat defines the different formats that can be parsed by Scalpel
    to retrieve the data about an experiment from the experiment-ware's output.
    """

    CSV = 'csv'
    CSV2 = 'csv2', 'csv-2'
    TSV = 'tsv', 'table'
    JSON = 'json'
    XML = 'xml'
    RAW_LOG = 'out', 'log'

    def is_csv(self):
        """
        Checks whether this format identifies a variant of the CSV format.

        :return: Whether this format is a CSV format.
        """
        return self in (OutputFormat.CSV,
                        OutputFormat.CSV2,
                        OutputFormat.TSV)
