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
This module provides various classes for parsing different types of files
containing the output of experiment-wares produced during a campaign, to
extract the data they contain.
"""


from json import load as load_json
from typing import Any, Optional, TextIO
from xml.etree.ElementTree import Element, parse as load_xml

from metrics.scalpel import CampaignParserListener
from metrics.scalpel.config import ScalpelConfiguration
from metrics.scalpel.utils import CsvConfiguration, CsvReader


class CampaignOutputParser:
    """
    The CampaignOutputParser is the parent class for the parsers used to
    read the output files produced by an experiment-ware during an experiment.
    """

    def __init__(self, listener: CampaignParserListener, file_path: str, file_name: str,
                 name_as_prefix: bool) -> None:
        """
        Creates a new CampaignOutputParser.

        :param listener: The listener to notify while parsing.
        :param file_path: The path of the file to parse.
        :param file_name: The name of the file to parse.
        :param name_as_prefix: Whether the name of the file must be used as a prefix for
                               identifying the read data.
        """
        self._listener = listener
        self._file_path = file_path
        self._file_name = file_name
        self._name_as_prefix = name_as_prefix

    def parse(self) -> None:
        """
        Parses the associated file.
        """
        with open(self._file_path, 'r', encoding='utf-8') as stream:
            self._internal_parse(stream)

    def _internal_parse(self, stream: TextIO) -> None:
        """
        Parses the given stream.

        :param stream: The stream to parse.
        """
        raise NotImplementedError('Method "_internal_parse()" is abstract!')

    def log_data(self, key: str, value: Any) -> None:
        """
        Notifies the listener about data that has been read about an experiment.

        :param key: The key identifying the read data.
        :param value: The value that has been read.
        """
        if self._name_as_prefix:
            self._listener.log_data(f'{self._file_name}.{key}', value)
        else:
            self._listener.log_data(key, value)


class CsvCampaignOutputParser(CampaignOutputParser):
    """
    The CsvCampaignOutputParser is a parser that reads a CSV output file
    produced by an experiment-ware during an experiment.
    """

    def __init__(self, listener: CampaignParserListener, file_path: str, file_name: str,
                 name_as_prefix: bool, config: CsvConfiguration = CsvConfiguration()) -> None:
        """
        Creates a new CsvCampaignOutputParser.

        :param listener: The listener to notify while parsing.
        :param file_path: The path of the file to parse.
        :param file_name: The name of the file to parse.
        :param name_as_prefix: Whether the name of the file must be used as a prefix for
                               identifying the read data.
        :param config: The configuration to apply when parsing the CSV file.
        """
        super().__init__(listener, file_path, file_name, name_as_prefix)
        self._configuration = config

    def _internal_parse(self, stream: TextIO) -> None:
        """
        Parses the given stream to extract data about the campaign.

        :param stream: The stream to read.
        """
        reader = CsvReader(stream, self._configuration)
        for line in reader.read():
            for key, value in line:
                self.log_data(key, value)


class MarkupCampaignOutputParser(CampaignOutputParser):
    """
    The MarkupCampaignOutputParser is the parent class of the parsers that parse
    campaign outputs written using some markup(-like) language.
    """

    def _internal_parse(self, stream: TextIO) -> None:
        """
        Parses the given stream to extract data about the campaign.

        :param stream: The stream to read.
        """
        self._decode(self._load_markup(stream))

    def _load_markup(self, stream: TextIO) -> Any:
        """
        Loads data from a stream written in a markup language.

        :param stream: The stream to load data from.

        :return: An object wrapping the content of the stream.
        """
        raise NotImplementedError('Method "_load_markup()" is abstract!')

    def _decode(self, obj: Any, prefix: Optional[str] = None) -> None:
        """
        Decodes an object wrapping the content of a stream encoded in a
        markup language to extract campaign data.

        :param obj: The object to decode.
        :param prefix: The prefix for the fields in the object.
        """
        raise NotImplementedError('Method "_decode()" is abstract!')

    @staticmethod
    def _create_prefix(prefix: Optional[str], field: Any) -> str:
        """
        Creates the prefix for a new field.

        :param prefix: The current prefix.
        :param field: The name of the field being explored.

        :return: The created prefix.
        """
        return str(field) if prefix is None else f'{prefix}.{field}'


class JsonCampaignOutputParser(MarkupCampaignOutputParser):
    """
    The JsonCampaignOutputParser is a parser that reads the output of an
    experiment from a JSON file produced by an experiment-ware.
    """

    def _load_markup(self, stream: TextIO) -> Any:
        """
        Loads data from a stream written in JSON.

        :param stream: The stream to load data from.

        :return: An object wrapping the content of the stream.
        """
        return load_json(stream)

    def _decode(self, obj: Any, prefix: Optional[str] = None) -> None:
        """
        Decodes an object wrapping the content of a JSON stream to extract
        campaign data.

        :param obj: The object to decode.
        :param prefix: The prefix for the fields in the object.
        """
        if isinstance(obj, list):
            self._decode_array(obj, prefix)

        elif isinstance(obj, dict):
            self._decode_object(obj, prefix)

        else:
            self.log_data(prefix, obj)

    def _decode_array(self, array: list, field: Optional[str]) -> None:
        """
        Explores the given JSON array, and notifies the listener during
        the exploration.

        :param array: The JSON array to explore.
        :param field: The name for the objects in the JSON array.
        """
        for elt in array:
            self._decode(elt, field)

    def _decode_object(self, obj: dict, prefix: Optional[str]) -> None:
        """
        Explores the given JSON object, and notifies the listener during
        the exploration.

        :param obj: The JSON object to explore.
        :param prefix: The prefix for the fields in the JSON object.
        """
        for key, value in obj.items():
            field = MarkupCampaignOutputParser._create_prefix(prefix, key)
            self._decode(value, field)


class XmlCampaignOutputParser(MarkupCampaignOutputParser):
    """
    The XmlCampaignOutputParser is a parser that reads the output of an
    experiment from an XML file produced by an experiment-ware.
    """

    def _load_markup(self, stream: TextIO) -> Element:
        """
        Loads data from a stream written in XML.

        :param stream: The stream to load data from.

        :return: An object wrapping the content of the stream.
        """
        return load_xml(stream).getroot()

    def _decode(self, obj: Element, prefix: Optional[str] = None) -> None:
        """
        Decodes an object wrapping the content of an XML stream to extract
        campaign data.

        :param obj: The object to decode.
        :param prefix: The prefix for the fields in the object.
        """
        name = MarkupCampaignOutputParser._create_prefix(prefix, obj.tag)

        if obj.text and obj.text.strip():
            self.log_data(name, obj.text.strip())

        for key, value in obj.attrib.items():
            self.log_data(MarkupCampaignOutputParser._create_prefix(name, key), value)

        for child in obj:
            self._decode(child, name)


class RawCampaignOutputParser(CampaignOutputParser):
    """
    The RawCampaignOutputParser is a parser that reads the raw output of an
    experiment-ware.
    """

    def __init__(self, listener: CampaignParserListener, file_path: str, file_name: str,
                 name_as_prefix: bool, configuration: ScalpelConfiguration) -> None:
        """
        Creates a new RawCampaignOutputParser.

        :param listener: The listener to notify while parsing.
        :param file_path: The path of the file to parse.
        :param file_name: The name of the file to parse.
        :param name_as_prefix: Whether the name of the file must be used as a prefix for
                               identifying the read data.
        :param configuration: The configuration describing how to extract data from the output file.
        """
        super().__init__(listener, file_path, file_name, name_as_prefix)
        self._configuration = configuration

    def _internal_parse(self, stream: TextIO) -> None:
        """
        Parses the given stream to extract data about the campaign.

        :param stream: The stream to read.
        """
        for line in stream:
            self._parse_line(line.rstrip())

    def _parse_line(self, line: str) -> None:
        """
        Parses the given line to extract data about the campaign.

        :param line: The line to read.
        """
        for log_data in self._configuration.get_data_in(self._file_name):
            # Extracting relevant data from the line.
            names = log_data.get_names()
            values = log_data.extract_value_from(line)

            # If there was no data in the line, there is nothing to do.
            if not values:
                continue

            # Unpacking and logging the read data.
            if len(names) == len(values):
                for name, value in zip(names, values):
                    self.log_data(name, value)
            else:
                name = names[0]
                for index, value in enumerate(values):
                    self.log_data(f'{name}{index}', value)
