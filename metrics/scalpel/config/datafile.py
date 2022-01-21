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
This module provides classes used to manage the data files from which Scalpel
will extract campaign data.
"""


from typing import Optional, Type

from metrics.scalpel.config.format import OutputFormat

from metrics.scalpel.utils import CsvConfiguration


class DataFile:
    """
    A DataFile object gathers all the information about a data-file to parse.
    """

    def __init__(self, name: str, name_as_prefix: bool, fmt: OutputFormat,
                 csv_configuration: Optional[CsvConfiguration], parser: Optional[Type]) -> None:
        """
        Creates a new DataFile.

        :param name: The name of the data-file.
        :param name_as_prefix: Whether the name of the data-file should be used as a prefix
                               to discriminate its content from the content of other files.
        :param fmt: The format of the data-file.
        :param csv_configuration: The CSV configuration of the data-file (only if the
                                  data-file uses the CSV format).
        :param parser: The custom parser to use to parse this data-file (if specified).
        """
        self._name = name
        self._name_as_prefix = name_as_prefix
        self._format = fmt
        self._csv_configuration = csv_configuration
        self._parser = parser

    def get_name(self) -> str:
        """
        Gives the name of this data-file.

        :return: The name of this data-file.
        """
        return self._name

    def has_name_as_prefix(self) -> bool:
        """
        Checks whether the name of this data-file should be used as a prefix
        to discriminate its content from the content of other files.

        :return: Whether the name of this data-file should be used as a prefix.
        """
        return self._name_as_prefix

    def get_format(self) -> OutputFormat:
        """
        Gives the format of this data-file.

        :return: The format of this data-file.
        """
        return self._format

    def get_csv_configuration(self) -> Optional[CsvConfiguration]:
        """
        Gives the CSV configuration of this data-file.

        :return: The CSV configuration of this data-file, or None if this
                 data-file is not in the CSV format.
        """
        return self._csv_configuration

    def get_custom_parser(self) -> Optional[Type]:
        """
        Gives the custom parser to use to parse this data-file.

        :return: The class of the parser for this data-file (if specified).
        """
        return self._parser
