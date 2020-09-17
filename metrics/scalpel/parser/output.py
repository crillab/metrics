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
This module provides various classes for parsing different types of files
containing the output of experiment-wares produced during a campaign, so as to
extract the data they contain.
"""


from json import load as load_json
from typing import Any, Optional, TextIO

from metrics.scalpel import CampaignParserListener
from metrics.scalpel.config import ScalpelConfiguration
from metrics.scalpel.parser.utils import CsvReader


class CampaignOutputParser:
    """
    The CampaignOutputParser is the parent class for the parsers used to
    read the output files produced by an experiment-ware during an experiment.
    """

    def __init__(self, listener: CampaignParserListener, file: str) -> None:
        """
        Creates a new CampaignOutputParser.

        :param listener: The listener to notify while parsing.
        :param file: The path of the file to parse.
        """
        self._listener = listener
        self._file = file

    def parse(self) -> None:
        """
        Parses the associated file.
        """
        with open(self._file, 'r') as stream:
            self._internal_parse(stream)

    def _internal_parse(self, stream: TextIO) -> None:
        """
        Parses the given stream.

        :param stream: The stream to parse.
        """
        raise NotImplementedError('Method "parse()" is abstract!')

    def log_data(self, key: str, value: str) -> None:
        """
        Notifies the listener about data that has been read about an experiment.

        :param key: The key identifying the read data.
        :param value: The value that has been read.
        """
        self._listener.log_data(key, value)


class CsvCampaignOutputParser(CampaignOutputParser):
    """
    The CsvCampaignOutputParser is a parser that reads a CSV output file
    produced by an experiment-ware during an experiment.
    """

    def __init__(self, listener: CampaignParserListener, file: str,
                 separator: str = ',', quote_char: Optional[str] = None) -> None:
        """
        Creates a new CsvCampaignOutputParser.

        :param listener: The listener to notify while parsing.
        :param file: The path of the file to parse.
        :param separator: The value separator used in the CSV input.
        :param quote_char: The character used to quote the fields in the
                           CSV input, if any.
        """
        super().__init__(listener, file)
        self._separator = separator
        self._quote_char = quote_char

    def _internal_parse(self, stream: TextIO) -> None:
        """
        Parses the given stream to extract data about the campaign.

        :param stream: The stream to read.
        """
        reader = CsvReader(stream, self._separator, self._quote_char)
        for line in reader.read():
            for key, value in line:
                self.log_data(key, value)


class JsonCampaignOutputParser(CampaignOutputParser):
    """
    The JsonCampaignOutputParser is a parser that reads the output of an
     experiment from a JSON file produced by an experiment-ware.
    """

    def _internal_parse(self, stream: TextIO) -> None:
        """
        Parses the given stream to extract data about the campaign.

        :param stream: The stream to read.
        """
        self._read(load_json(stream))

    def _read(self, json: Any, prefix: Optional[str] = None) -> None:
        """
        Reads data from a (JSON) object by recursively exploring it.

        :param json: The JSON object to explore.
        :param prefix: The prefix for the fields in the JSON object.
        """
        if isinstance(json, list):
            self._read_array(json, prefix)

        elif isinstance(json, dict):
            self._read_object(json, prefix)

        else:
            self._listener.log_data(prefix, str(json))

    def _read_object(self, obj: dict, prefix: Optional[str]) -> None:
        """
        Explores the given JSON object, and notifies the listener during
        the exploration.

        :param obj: The JSON object to explore.
        :param prefix: The prefix of the fields in the JSON object.
        """
        for key, value in obj.items():
            new_prefix = JsonCampaignOutputParser._create_prefix(prefix, key)
            self._read(value, new_prefix)

    def _read_array(self, array: list, field: Optional[str]) -> None:
        """
        Explores the given JSON array, and notifies the listener during
        the exploration.

        :param array: The JSON array to explore.
        :param field: The name of the field corresponding to the JSON array.
        """
        for elt in array:
            self._read(elt, field)

    @staticmethod
    def _create_prefix(prefix: Optional[str], field: Any) -> str:
        """
        Creates the prefix for a new field.

        :param prefix: The current prefix.
        :param field: The name of the field being explored.

        :return: The created prefix.
        """
        return str(field) if prefix is None else f'{prefix}.{field}'


class RawCampaignOutputParser(CampaignOutputParser):
    """
    The RawCampaignOutputParser is a parser that reads the raw output of an
    experiment-ware.
    """

    def __init__(self, configuration: ScalpelConfiguration,
                 listener: CampaignParserListener,
                 file: str, file_path: str) -> None:
        """
        Creates a new RawCampaignOutputParser.

        :param configuration: The configuration describing how to extract
               data from the output file.
        :param listener: The listener to notify while parsing.
        :param file: The name of the file to parse.
        :param file_path: The path of the file to parse.
        """
        super().__init__(listener, file_path)
        self._configuration = configuration
        self._file_name = file

    def _internal_parse(self, stream: TextIO) -> None:
        """
        Parses the given stream to extract data about the campaign.

        :param stream: The stream to read.
        """
        for line in stream:
            self._parse_line(line)

    def _parse_line(self, line: str) -> None:
        """
        Parses the given line to extract data about the campaign.

        :param line: The line to read.
        """
        for log_data in self._configuration.get_data_in(self._file_name):
            value = log_data.extract_value_from(line)
            if value is not None:
                self.log_data(log_data.get_name(), value)
