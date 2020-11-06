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
This module provides utility classes making easier the parsing of different
types of files.
"""


from typing import Callable, Iterable, List, TextIO, Tuple
from warnings import warn

from metrics.scalpel.config.config import CsvConfiguration


class CsvReader:
    """
    The CsvReader allows to easily parse CSV files that may have a header
    line, describing what the columns contain.
    """

    def __init__(self, stream: TextIO, configuration: CsvConfiguration,
                 row_filter: Callable[[List[str]], bool] = lambda r: True) -> None:
        """
        Creates a new CsvReader.

        :param stream: The stream to read as a CSV input.
        :param configuration: The configuration of the reader.
        :param row_filter: The filter allowing to select which rows to consider
                           from the CSV stream.
        """
        self._stream = stream
        self._configuration = configuration
        self._row_filter = row_filter
        self._line_iterator = None
        self._keys = []
        self._cache = None

    def read(self) -> Iterable[List[Tuple[str, str]]]:
        """
        Parses the associated CSV stream to extract data from this stream.

        :return: The data collected from the stream, given by key-value pairs.
        """
        self.read_header()
        return self.read_content()

    def read_header(self) -> List[str]:
        """
        Parses the associated CSV stream to extract its header.

        :return: The header of the CSV stream.
        """
        self._line_iterator = iter(self._configuration.create_loader(self._stream))
        if self._configuration.has_header():
            self._keys = next(self._line_iterator)
        else:
            self._cache = next(self._line_iterator)
            self._keys = [str(i) for i in range(len(self._cache))]
        return self._keys

    def read_content(self) -> Iterable[List[Tuple[str, str]]]:
        """
        Parses the associated CSV stream to extract its content.

        :return: The content of the CSV stream.
        """
        for index, line in self._read_lines():
            line = list(map(str.strip, line))
            if len(line) == len(self._keys):
                yield zip(self._keys, line)
            else:
                warn(f'Line #{index} does not match header: {line}')

    def _read_lines(self) -> Iterable[Tuple[int, List[str]]]:
        """
        Reads the associated CSV stream and only yields relevant lines.

        :return: The relevant lines from the CSV stream, and their index in
                 this stream.
        """
        if self._cache is not None and self._row_filter(self._cache):
            yield 1, self._cache

        for index, line in enumerate(self._line_iterator):
            if self._row_filter(line):
                yield 2 + index, line
