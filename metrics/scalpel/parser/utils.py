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
This module provides utility classes wrapping the readers from the standard
library to better fit Scalpel's needs.
"""


from csv import reader as load_csv
from typing import Callable, Iterable, Iterator, List, Optional, TextIO, Tuple


class CsvReader:
    """
    The CsvReader allows to easily parse CSV files having a header line,
    describing what the columns contain.
    """

    def __init__(self, stream: TextIO, separator: str = ',',
                 quote_char: Optional[str] = None,
                 row_filter: Callable[[List[str]], bool] = lambda r: True) -> None:
        """
        Creates a new CsvReader.

        :param stream: The stream to read as a CSV input.
        :param separator: The value separator, which is ',' by default.
        :param quote_char: The character used to quote the fields in the
                           CSV file, if any.
        :param row_filter: The filter allowing to select which rows to consider
                           from the CSV stream.
        """
        self._stream = stream
        self._separator = separator
        self._quote_char = quote_char
        self._row_filter = row_filter
        self._keys = []

    def read(self) -> Iterable[List[Tuple[str, str]]]:
        """
        Parses the associated stream to extract data from this stream.

        :return: The data collected from the CSV file, given by key-value pairs.
        """
        for line in self._internal_read():
            line = list(map(str.strip, line))
            mapped = self._parse_line(line)
            if mapped is not None:
                yield mapped

    def _internal_read(self) -> Iterable[List[str]]:
        """
        Reads the associated CSV stream line-by-line.

        :return: The lines of the CSV stream.
        """
        if self._quote_char is None:
            return load_csv(self._stream, delimiter=self._separator)

        return load_csv(self._stream, delimiter=self._separator,
                        quotechar=self._quote_char)

    def _parse_line(self, line: List[str]) -> Optional[Iterator[Tuple[str, str]]]:
        """
        Parses the given line to extract the data it contains.

        :param line: The line to parse.
        """
        if not self._keys:
            # The header has not been read yet.
            self._keys = line

        elif self._row_filter(line):
            # Reading the values of this line.
            return zip(self._keys, line)
