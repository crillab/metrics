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
containing the results of a campaign, so as to build its representation.
"""


from csv import reader as load_csv
from os import path, scandir
from typing import Iterable, List, Optional, TextIO

from metrics.scalpel.config import ScalpelConfiguration
from metrics.scalpel.config.format import OutputFormat
from metrics.scalpel.listener import CampaignParserListener
from metrics.scalpel.parser.output import CampaignOutputParser, \
    CsvCampaignOutputParser, JsonCampaignOutputParser, RawCampaignOutputParser


class CampaignParser:
    """
    The CampaignParser is the parent class of all the parsers allowing to read
    the results of a campaign.
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
        raise NotImplementedError('Method "parse_file()" is abstract!')

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


class FileCampaignParser(CampaignParser):
    """
    The FileCampaignParser is the parent class of all the parsers allowing to
    read the results of a campaign from a (regular) file.
    """

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


class CsvCampaignParser(FileCampaignParser):
    """
    The CsvCampaignParser is a parser that reads the output of a campaign from
    a CSV file.
    """

    def __init__(self, listener: CampaignParserListener, separator: str = ',',
                 quote_char: Optional[str] = None) -> None:
        """
        Creates a new CsvCampaignParser.

        :param listener: The listener to notify while parsing.
        :param separator: The value separator, which is ',' by default.
        :param quote_char: The character used to quote the fields in the
                           CSV file.
        """
        super().__init__(listener)
        self._separator = separator
        self._quote_char = quote_char
        self._keys = []

    def parse_stream(self, stream: TextIO) -> None:
        """
        Parses the given stream to extract data about the campaign.

        :param stream: The stream to read.
        """
        for line in self._parse_csv(stream):
            line = list(map(str.strip, line))
            self._parse_line(line)

    def _parse_csv(self, stream: TextIO) -> Iterable[List[str]]:
        """
        Reads the given stream as a CSV file.

        :param stream: The stream to read.

        :return: The lines of the read CSV file.
        """
        if self._quote_char is None:
            return load_csv(stream, delimiter=self._separator)

        return load_csv(stream, delimiter=self._separator,
                        quotechar=self._quote_char)

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
                for key, value in zip(self._keys, values):
                    self.log_data(key, value)
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

    def parse_file(self, file_path: str) -> None:
        """
        Explores the directory at the given path, considered as the root
        directory of the campaign.

        :param file_path: The path of the directory to explore.
        """
        self.explore(file_path)

    def explore(self, root: str) -> None:
        """
        Explores the file hierarchy rooted at the given directory.

        :param root: The root directory of the file hierarchy to explore.
        """
        raise NotImplementedError('Method "explore()" is abstract!')

    def _get_parser_for(self, file: str, file_path: str) -> CampaignOutputParser:
        """
        Gives the parser to use to extract data from the given file.

        :param file: The name of the file to get the parser for.
        :param file_path: The path of the file to get the parser for.

        :return: The parser to use.
        """
        fmt = DirectoryCampaignParser._guess_format(file)

        if fmt == OutputFormat.CSV:
            return CsvCampaignOutputParser(self._listener, file_path)

        if fmt == OutputFormat.CSV2:
            return CsvCampaignOutputParser(self._listener, file_path, ';')

        if fmt == OutputFormat.TSV:
            return CsvCampaignOutputParser(self._listener, file_path, '\t')

        if fmt == OutputFormat.JSON:
            return JsonCampaignOutputParser(self._listener, file_path)

        return RawCampaignOutputParser(self._configuration, self._listener,
                                       file, file_path)

    @staticmethod
    def _guess_format(file: str) -> OutputFormat:
        """
        Guesses the format of the given file.

        :param file: The file to guess the format of.

        :return: The format of the file.
        """
        try:
            index = file.rindex('.')
            return OutputFormat.value_of(file[index + 1:])
        except ValueError:
            return OutputFormat.RAW_LOG


class DeepDirectoryCampaignParser(DirectoryCampaignParser):
    """
    The DeepDirectoryCampaignParser allows to extract the data collected during
    a campaign by recursively exploring an entire file hierarchy.
    """

    def __init__(self, configuration: ScalpelConfiguration,
                 listener: CampaignParserListener,
                 depth: int = 1) -> None:
        """
        Creates a new DeepDirectoryCampaignParser.

        :param configuration: The configuration describing how to extract
               data from the output file.
        :param listener: The listener to notify while parsing.
        :param depth: The depth to explore in the file hierarchy.
        """
        super().__init__(configuration, listener)
        self._depth = depth

    def explore(self, root: str) -> None:
        """
        Explores the file hierarchy rooted at the given directory.

        :param root:  The root directory of the file hierarchy to explore.
        """
        self.recursive_explore(root, 0)

    def recursive_explore(self, directory: str, depth: int) -> None:
        """
        Recursively explores the file hierarchy rooted at the given directory.

        :param directory: The directory to explore
        :param depth: The depth to explore starting from the directory.
        """
        if depth == self._depth:
            self._explore_experiment(directory)

        elif path.isdir(directory):
            with scandir(directory) as current_dir:
                for subdir in current_dir:
                    subdir_path = path.join(directory, subdir.name)
                    self.recursive_explore(subdir_path, depth + 1)

    def _explore_experiment(self, directory: str) -> None:
        """
        Explores the output files of an experiment, stored in the given
        directory.

        :param directory: The directory of the experiment.
        """
        with scandir(directory) as experiment:
            self.start_experiment()
            for file in experiment:
                if self._configuration.is_to_be_parsed(file.name):
                    self._parse_file(directory, file.name)
            self.end_experiment()

    def _parse_file(self, directory: str, file: str) -> None:
        """
        Parses an output file of the campaign.

        :param directory: The directory of the experiment being considered.
        :param file: The file to consider.
        """
        file_path = path.join(directory, file)
        if path.exists(file_path):
            parser = self._get_parser_for(file, file_path)
            parser.parse()


class FlatDirectoryCampaignParser(DirectoryCampaignParser):
    """
    The FlatDirectoryCampaignParser allows to extract the data collected during
    a campaign when they are stored in a single directory, in which all files
    correspond to exactly one experiment.
    """

    def __init__(self, configuration: ScalpelConfiguration,
                 listener: CampaignParserListener) -> None:
        """
        Creates a new FlatDirectoryCampaignParser.

        :param configuration: The configuration describing how to extract
               data from the output file.
        :param listener: The listener to notify while parsing.
        """
        super().__init__(configuration, listener)

    def explore(self, root: str) -> None:
        """
        Explores the file hierarchy rooted at the given directory.

        :param root:  The root directory of the file hierarchy to explore.
        """
        with scandir(root) as root_dir:
            for file in root_dir:
                self.start_experiment()
                parser = self._get_parser_for(file.name, path.join(root, file.name))
                parser.parse()
                self.end_experiment()
