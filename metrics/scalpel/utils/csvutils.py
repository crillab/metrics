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
This module provides utility classes making easier the parsing of CSV files.
"""


from csv import reader as load_csv
from typing import Callable, Iterable, List, Optional, TextIO, Tuple

from metrics.scalpel.utils.logging import logger


class CsvConfiguration:
    """
    The CsvConfiguration provides a convenient way to configure how a CSV stream should be parsed.
    """

    def __init__(self, has_header: bool = True, quote_char: Optional[str] = None,
                 separator: str = ',', title_separator: str = '.') -> None:
        """
        Creates a new CsvConfiguration.

        :param has_header: Whether the input stream to parse has a header.
        :param quote_char: The quote character used to escape special characters in the
                           stream to parse.
        :param separator: The separator used to distinguish different fields in the
                          stream to parse.
        :param title_separator: The separator used to distinguish different elements in the
                                titles of the stream to parse.
        """
        self._has_header = has_header
        self._quote_char = quote_char
        self._separator = separator
        self._title_separator = title_separator

    def has_header(self) -> bool:
        """
        Checks whether the input stream to parse has a header.

        :return: If the input stream to parse has a header.
        """
        return self._has_header

    def get_quote_char(self) -> Optional[str]:
        """
        Gives the quote character used to escape special characters in the stream to parse.

        :return: The quote character that is used (if specified).
        """
        return self._quote_char

    def get_separator(self) -> str:
        """
        Gives the separator used to distinguish different fields in the stream to parse.

        :return: The separator that is used.
        """
        return self._separator

    def get_title_separator(self) -> str:
        """
        Gives the separator used to distinguish different elements in the titles of the
        stream to parse.

        :return: The title separator that is used (if specified).
        """
        return self._title_separator


class CsvReader:
    """
    The CsvReader allows to easily parse CSV files that may have a header line
    describing what the columns contain.
    """

    def __init__(self, stream: TextIO, configuration: CsvConfiguration,
                 row_filter: Callable[[List[str]], bool] = lambda r: True) -> None:
        """
        Creates a new CsvReader.

        :param stream: The stream to read as a CSV input.
        :param configuration: The configuration of the CSV file.
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
        self._line_iterator = iter(self._create_loader())
        if self._configuration.has_header():
            self._keys = [k.strip() for k in next(self._line_iterator)]
        else:
            self._cache = next(self._line_iterator)
            self._keys = [str(i) for i in range(len(self._cache))]
        logger.trace(f'keys {self._keys} inferred from CSV header')
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
                logger.warning(f'ignoring line #{index} which does not match the header: {line}')

    def _read_lines(self) -> Iterable[Tuple[int, List[str]]]:
        """
        Reads the associated CSV stream and only yields relevant lines.

        :return: The relevant lines from the CSV stream, and their index in this stream.
        """
        if self._cache is not None and self._row_filter(self._cache):
            yield 1, self._cache

        for index, line in enumerate(self._line_iterator):
            if self._row_filter(line):
                yield 2 + index, line

    def _create_loader(self) -> Iterable[List[str]]:
        """
        Creates a loader for reading the associated CSV stream.

        :return: The loader for the CSV stream.
        """
        if self._configuration.get_quote_char() is None:
            return load_csv(self._stream, delimiter=self._configuration.get_separator())

        return load_csv(self._stream, delimiter=self._configuration.get_separator(),
                        quotechar=self._configuration.get_quote_char())
