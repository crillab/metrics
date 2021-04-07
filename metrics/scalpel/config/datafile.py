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
This module provides classes used to manage the data files from which Scalpel
will extract campaign data.
"""


from pydoc import locate

from metrics.scalpel.config.format import OutputFormat


class DataFile:
    """
    A DataFile object gathers all the information about a data-file to parse.
    """

    def __init__(self, name: str, name_as_prefix, fmt: OutputFormat, csv_configuration, parser: str):
        self._name = name
        self._format = fmt
        self._csv_configuration = csv_configuration
        self._parser = parser
        self._name_as_prefix = name_as_prefix

    def get_name(self):
        return self._name

    def get_format(self):
        if self._format is None:
            self._format = OutputFormat.guess_format(self._name)
        return self._format

    def get_configuration(self):
        return self._csv_configuration

    def get_parser(self):
        if self._parser is None:
            return None
        return locate(self._parser)

    def has_name_as_prefix(self):
        return self._name_as_prefix


def create_data_file(file_name, name_as_prefix=False, fmt=None, csv_config=None, parser=None):
    return DataFile(file_name, name_as_prefix, fmt, csv_config, parser)
