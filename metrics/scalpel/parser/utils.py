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
This module provides utility classes wrapping standard readers to better fit
Scalpel's needs.
"""


from csv import reader as load_csv
from typing import Callable, Iterable, List, Optional, TextIO, Tuple


class CsvReader:
    """
    The CsvReader allows to easily parse CSV files that may have a header
    line, describing what the columns contain.
    """

    def __init__(self, stream: TextIO,
                 separator: str = ',',
                 quote_char: Optional[str] = None,
                 has_header: bool = True,
                 row_filter: Callable[[List[str]], bool] = lambda r: True) -> None:
        """
        Creates a new CsvReader.

        :param stream: The stream to read as a CSV input.
        :param separator: The value separator used in the CSV input.
        :param quote_char: The character used to quote the fields in the
                           CSV input, if any.
        :param has_header: Whether the CSV input has a header line.
        :param row_filter: The filter allowing to select which rows to consider
                           from the CSV stream.
        """
        self._stream = stream
        self._separator = separator
        self._quote_char = quote_char
        self._has_header = has_header
        self._row_filter = row_filter
        self._line_iterator = None
        self._keys = []
        self._cache = None

    def read(self) -> Iterable[List[Tuple[str, str]]]:
        """
        Parses the associated CSV stream to extract data from this stream.

        :return: The data collected from the stream, given by key-value pairs.

        :raises ValueError: If one of the lines does not match the header.
        """
        self.read_header()
        return self.read_content()

    def read_header(self) -> List[str]:
        """
        Parses the associated CSV stream to extract its header.

        :return: The header of the CSV stream.
        """
        self._line_iterator = iter(self._internal_read())
        if self._has_header:
            self._keys = next(self._line_iterator)
        else:
            self._cache = next(self._line_iterator)
            self._keys = [str(i) for i in range(len(self._cache))]
        return self._keys

    def read_content(self) -> Iterable[List[Tuple[str, str]]]:
        """
        Parses the associated CSV stream to extract its content.

        :return: The content of the CSV stream.

        :raises ValueError: If one of the lines does not match the header.
        """
        for index, line in self._read_lines():
            line = list(map(str.strip, line))
            if len(line) != len(self._keys):
                raise ValueError(f'Line #{index} does not match header: {line}')
            yield zip(self._keys, line)

    def _read_lines(self) -> Iterable[Tuple[int, List[str]]]:
        """
        Reads the associated CSV stream and only yields relevant lines.

        :return: The relevant lines from the CSV stream, and their index in
                 this stream.
        """
        if self._cache is not None:
            yield 1, self._cache

        for index, line in enumerate(self._line_iterator):
            if self._row_filter(line):
                yield 2 + index, line

    def _internal_read(self) -> Iterable[List[str]]:
        """
        Reads the associated CSV stream line-by-line.

        :return: The lines of the CSV stream.
        """
        if self._quote_char is None:
            return load_csv(self._stream, delimiter=self._separator)

        return load_csv(self._stream, delimiter=self._separator, quotechar=self._quote_char)
