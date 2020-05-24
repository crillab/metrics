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
containing the output of a campaign, so as to build its representation.
"""


from csv import reader as read_csv
from os import path, scandir
from pydoc import locate
from typing import List, Optional, TextIO, Iterable

from metrics.scalpel.listener import CampaignParserListener
from metrics.scalpel.config import ScalpelConfiguration, CampaignFormat


class CampaignParser:
    """
    The CampaignParser is the parent class of all the parsers allowing to read
    the output files of a campaign.
    """

    def __init__(self, listener: CampaignParserListener) -> None:
        """
        Creates a new CampaignParser.

        :param listener: The listener to notify while parsing.
        """
        self._listener = listener

    def parse_file(self, file_path: str) -> None:
        """
        Parses the file at the given path to extract data about the campaign.

        :param file_path: The path of the file to read.
        """
        with open(file_path) as file:
            self.parse_stream(file)

    def parse_stream(self, stream: TextIO) -> None:
        """
        Parses the given stream to extract data about the campaign.

        :param stream: The stream to read.
        """
        raise NotImplementedError('Method "parse_stream()" is abstract!')

    def start_experiment(self) -> None:
        """
        Notifies the listener that a new experiment is being parsed.
        """
        self._listener.start_experiment()

    def log_data(self, key: str, value: str) -> None:
        """
        Notifies the listener about data that has been read about an experiment.

        :param key: The key identifying the read data.
        :param value: The value that has been read.
        """
        self._listener.log_data(key, value)

    def end_experiment(self) -> None:
        """
        Notifies the listener that the current experiment has been fully parsed.
        """
        self._listener.end_experiment()


class CsvCampaignParser(CampaignParser):
    """
    The CsvCampaignParser is a parser that reads the output of a campaign from
    a CSV file.
    """

    def __init__(self, listener: CampaignParserListener, separator: str = ',',
                 quotechar: Optional[str] = None) -> None:
        """
        Creates a new CsvCampaignParser.

        :param listener: The listener to notify while parsing.
        :param separator: The value separator, which is ',' by default.
        :param quotechar: The character used to quote the fields in the CSV file.
        """
        super().__init__(listener)
        self._separator = separator
        self._quotechar = quotechar
        self._keys = []

    def parse_stream(self, stream: TextIO) -> None:
        """
        Parses the given stream to extract data about the campaign.

        :param stream: The stream to read.
        """
        for line in self._read_csv(stream):
            line = list(map(str.strip, line))
            self._parse_line(line)

    def _read_csv(self, stream: TextIO) -> Iterable[List[str]]:
        """
        Reads the given stream as a CSV file.

        :param stream: The stream to read.

        :return: The lines of the read CSV file.
        """
        if self._quotechar is None:
            return read_csv(stream, delimiter=self._separator)
        return read_csv(stream, delimiter=self._separator, quotechar=self._quotechar)

    def _parse_line(self, line: List[str]) -> None:
        """
        Parses the given line to extract data about an experiment.

        :param line: The line to parse.
        """
        if not self._keys:
            # The header has not been read yet.
            self._keys = self.parse_header(line)
        else:
            # Reading the values of this line.
            values = self.parse_xp_line(line)
            if values:
                self.start_experiment()
                for key_value in zip(self._keys, values):
                    self.log_data(key_value[0], key_value[1])
                self.end_experiment()

    def parse_header(self, line: List[str]) -> List[str]:
        """
        Parses the given line as the header of the file.
        By default, the line is returned without any modification.

        :param line: The line to parse.

        :return: The list of keys declared in the header.
        """
        return line

    def parse_xp_line(self, line: List[str]) -> List[str]:
        """
        Parses the given line as an experiment.
        By default, the line is returned without any modification.

        :param line: The line to parse.

        :return: The list of the values in the line, or an empty list if the
                 line does not contain any relevant information.
        """
        return line


class EvaluationCampaignParser(CsvCampaignParser):
    """
    The EvaluationCampaignParser is a parser that reads the output of a
    campaign produced by the Evaluation platform.
    """

    def __init__(self, listener: CampaignParserListener) -> None:
        """
        Creates a new EvaluationCampaignParser.

        :param listener: The listener to notify while parsing.
        """
        super().__init__(listener, '|')

    def parse_xp_line(self, line: List[str]) -> List[str]:
        """
        Parses the given line as an experiment.

        :param line: The line to parse.

        :return: The list of the values in the line, or an empty list if the
                 line does not contain any relevant information.
        """
        if len(line) == 1:
            return []
        return line


class JsonCampaignParser(CampaignParser):
    """
    The JsonCampaignParser is a parser that reads the output of a campaign from
    a JSON file, which has been previously produced by Metrics.
    """

    def parse_stream(self, stream: TextIO) -> None:
        """
        Parses the given stream to extract data about the campaign.

        :param stream: The stream to read.
        """
        raise NotImplementedError('Not implemented yet!')


class LineBasedCampaignParser(CampaignParser):
    """
    The LineBasedCampaignParser is the parent class of the parsers that read
    files line by line.
    """

    def parse_stream(self, stream: TextIO) -> None:
        """
        Parses the given stream to extract data about the campaign.

        :param stream: The stream to read.
        """
        for line in stream:
            self.parse_line(line)

    def parse_line(self, line: str) -> None:
        """
        Parses the given line to extract data about the campaign.

        :param line: The line to read.
        """
        raise NotImplementedError('Method "parse_line()" is abstract!')


class ExperimentWareOutputCampaignParser(LineBasedCampaignParser):
    """
    The ExperimentWareOutputCampaignParser is a parser that reads the raw
    output of an experiment-ware.
    """

    def __init__(self, configuration: ScalpelConfiguration,
                 listener: CampaignParserListener) -> None:
        """
        Creates a new ExperimentWareOutputCampaignParser.

        :param configuration: The configuration describing how to extract
               data from the output file.
        :param listener: The listener to notify while parsing.
        """
        super().__init__(listener)
        self._configuration = configuration
        self._current_file = None

    def now_parsing(self, current_file: str) -> None:
        """
        Notifies this parser that it is now parsing the file with the given
        name.
        Note that only the name of the file is considered (not the path of
        the file).

        :param current_file: The name of the file that is currently parsed.
        """
        self._current_file = current_file

    def parse_line(self, line: str) -> None:
        """
        Parses the given line to extract data about the campaign.

        :param line: The line to read.
        """
        for log_data in self._configuration.get_data_in(self._current_file):
            value = log_data.extract_value_from(line)
            if value is not None:
                self.log_data(log_data.get_name(), value)


class DirectoryCampaignParser(CampaignParser):
    """
    The DirectoryCampaignParser explores a file hierarchy containing all the
    output files produced during a campaign.
    """

    def __init__(self, configuration: ScalpelConfiguration,
                 listener: CampaignParserListener) -> None:
        """
        Creates a new DirectoryCampaignParser.

        :param configuration: The configuration describing how to extract
               data from the output file.
        :param listener: The listener to notify while parsing.
        """
        super().__init__(listener)
        self._configuration = configuration
        self._parser = ExperimentWareOutputCampaignParser(configuration, listener)

    def parse_file(self, file_path: str) -> None:
        """
        Explores the directory at the given path, considered as the root directory of
        the campaign.

        :param file_path: The path of the directory to explore.
        """
        self.explore_campaign(file_path)

    def parse_stream(self, stream: TextIO) -> None:
        """

        :param stream:
        """
        raise TypeError('DirectoryCampaignParser does not support stream parsing!')

    def explore_campaign(self, directory: str) -> None:
        """
        Explores the given directory as the root directory of the campaign.

        :param directory: The directory to explore.
        """
        with scandir(directory) as campaign:
            for experiment_ware in campaign:
                xp_ware_path = path.join(directory, experiment_ware.name)
                self._explore_experiment_ware(xp_ware_path)

    def _explore_experiment_ware(self, directory: str) -> None:
        """
        Explores the given directory as a set of experiments performed with the
        same experiment-ware during the campaign.

        :param directory: The directory to explore.
        """
        with scandir(directory) as experiment_ware:
            for experiment in experiment_ware:
                xp_path = path.join(directory, experiment.name)
                self._explore_experiment(xp_path)

    def _explore_experiment(self, directory: str) -> None:
        """
        Explores the output files of an experiment, stored in the given
        directory.

        :param directory: The directory of the experiment.
        """
        self._parser.start_experiment()
        for file in self._configuration.get_files():
            self._parse_file(directory, file)
        self._parser.end_experiment()

    def _parse_file(self, directory: str, file: str) -> None:
        """
        Parses an output file of the campaign.

        :param directory: The directory of the experiment being considered.
        :param file: The file to consider.
        """
        file_path = path.join(directory, file)
        if path.exists(file_path):
            self._parser.now_parsing(file)
            self._parser.parse_file(file_path)


def create_parser(config: ScalpelConfiguration, listener: CampaignParserListener) -> CampaignParser:
    """
    Creates the most appropriate parser to use to parse the campaign described
    in the given configuration.

    :param config: The configuration describing the campaign to parse.
    :param listener: The listener to notify while parsing.

    :return: The parser to use to parse the campaign.
    """
    # If the user has written their own parser, we use it.
    custom_parser = config.get_custom_parser()
    if custom_parser is not None:
        return locate(custom_parser)(config, listener)

    # Otherwise, we use one of the default parsers.
    campaign_format = config.get_format()

    if campaign_format == CampaignFormat.CSV:
        return CsvCampaignParser(listener)

    if campaign_format == CampaignFormat.CSV2:
        return CsvCampaignParser(listener, separator=';')

    if campaign_format == CampaignFormat.TSV:
        return CsvCampaignParser(listener, separator='\t')

    if campaign_format == CampaignFormat.EVALUATION:
        return EvaluationCampaignParser(listener)

    if campaign_format == CampaignFormat.RAW_LOG:
        return ExperimentWareOutputCampaignParser(config, listener)

    if campaign_format == CampaignFormat.FLAT_LOG_DIRECTORY:
        return DirectoryCampaignParser(config, listener)

    if campaign_format == CampaignFormat.DEEP_LOG_DIRECTORY:
        return DirectoryCampaignParser(config, listener)

    raise ValueError(f'Unrecognized input format: {campaign_format}')
