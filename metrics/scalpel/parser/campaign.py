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


from __future__ import annotations

from glob import glob
from os import path, scandir
from os.path import basename, splitext
from typing import Any, List, TextIO

from metrics.scalpel.config import ScalpelConfiguration
from metrics.scalpel.config.config import FileNameMetaConfiguration, CsvConfiguration
from metrics.scalpel.config.format import OutputFormat
from metrics.scalpel.listener import CampaignParserListener
from metrics.scalpel.parser.output import CampaignOutputParser, \
    CsvCampaignOutputParser, JsonCampaignOutputParser, XmlCampaignOutputParser, \
    RawCampaignOutputParser
from metrics.scalpel.parser.utils import CsvReader


class CampaignParserListenerNotifier:
    """
    The CampaignParserListenerNotifier is utility class allowing to easily
    notify a CampaignParserListener about parsing events, whatever how parsing
    is achieved.
    """

    def __init__(self, listener: CampaignParserListener,
                 file_name_meta: FileNameMetaConfiguration) -> None:
        """
        Creates a new CampaignParserListenerNotifier.

        :param listener: The listener to notify while parsing.
        :param file_name_meta: The configuration object describing how to
                               extract metadata from the path of the
                               parsed files.
        """
        self._listener = listener
        self._file_name_meta = file_name_meta
        self._file_name_data = {}

    def update_file_name_data(self, file: str) -> None:
        """
        Extracts the metadata from the name of the given file, and updates
        the metadata that have already been collected accordingly.

        :param file: The file to extract metadata from.
        """
        extracted_data = self._file_name_meta.extract_from(file)
        self._file_name_data.update(extracted_data)

    def reset_file_name_data(self) -> None:
        """
        Resets the metadata that have been extracted from the name of the
        files that have been parsed.
        """
        self._file_name_data = {}

    def start_experiment(self) -> None:
        """
        Notifies the listener that a new experiment is being parsed.
        """
        self._listener.start_experiment()

    def log_data(self, key: str, value: Any) -> None:
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
        for key, value in self._file_name_data.items():
            self.log_data(key, value)
        self._listener.end_experiment()


class CampaignParser:
    """
    The CampaignParser is the parent class of all the parsers allowing to read
    the results of a campaign.
    """

    def parse_file(self, file_path: str) -> None:
        """
        Parses the file at the given path to extract data about the campaign.

        :param file_path: The path of the file to read.
        """
        raise NotImplementedError('Method "parse_file()" is abstract!')


class FileCampaignParser(CampaignParserListenerNotifier, CampaignParser):
    """
    The FileCampaignParser is the parent class of all the parsers allowing to
    read the results of a campaign from a (regular) file.
    """

    def parse_file(self, file_path: str) -> None:
        """
        Parses the file at the given path to extract data about the campaign.

        :param file_path: The path of the file to read.
        """
        self.update_file_name_data(file_path)
        with open(file_path, 'r') as file:
            self.parse_stream(file)
        self.reset_file_name_data()

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

    def __init__(self, listener: CampaignParserListener, file_name_meta: FileNameMetaConfiguration,
                 csv_configuration: CsvConfiguration) -> None:
        """
        Creates a new CsvCampaignParser.

        :param listener: The listener to notify while parsing.
        :param file_name_meta: The configuration object describing how to
                               extract metadata from the path of the file to
                               parse.
        :param csv_configuration: The configuration for the CSV reader.
        """
        super().__init__(listener, file_name_meta)
        self.csv_configuration = csv_configuration
        self._reader = None

    def parse_stream(self, stream: TextIO) -> None:
        """
        Parses the given stream to extract data about the campaign.

        :param stream: The stream to read.
        """
        self.parse_header(stream)
        self.parse_content()

    def parse_header(self, stream: TextIO) -> List[str]:
        """
        Parses the header of a CSV stream.

        :param stream: The stream to read.

        :return: The header of the CSV stream
        """
        self._reader = CsvReader(stream, self.csv_configuration, self._row_filter)
        return self._reader.read_header()

    def parse_content(self) -> None:
        """
        Parses the content of a CSV stream using the associated reader.
        This reader must have been initialized using "parse_header()" before
        invoking this method.
        """
        for line in self._reader.read_content():
            self.start_experiment()
            for key, value in line:
                self.log_data(key, value)
            self.end_experiment()

    def _row_filter(self, row: List[str]) -> bool:
        """
        Checks whether the given row is relevant for the purpose of the
        campaign.

        :param row: The row to check.

        :return: Whether the given row is relevant.
        """
        return True


class EvaluationCampaignParser(CsvCampaignParser):
    """
    The EvaluationCampaignParser is a parser that reads the output of a
    campaign produced by the Evaluation platform.
    """

    def __init__(self, listener: CampaignParserListener,
                 file_name_meta: FileNameMetaConfiguration) -> None:
        """
        Creates a new EvaluationCampaignParser.

        :param listener: The listener to notify while parsing.
        :param file_name_meta: The configuration object describing how to
                               extract metadata from the path of the file to
                               parse.
        """
        super().__init__(listener, file_name_meta, CsvConfiguration('|'))

    def _row_filter(self, row: List[str]) -> bool:
        """
        Checks whether the given row is relevant for the purpose of the
        campaign.

        :param row: The row to check.

        :return: Whether the given row is relevant.
        """
        return len(row) > 1


class DirectoryCampaignParser(CampaignParser):
    """
    The DirectoryCampaignParser is a parser that explores a complete file
    hierarchy to extract the results of a campaign from the (regular) files
    it contains.
    """

    def __init__(self, file_exploration_strategy: FileExplorationStrategy) -> None:
        """
        Creates a new DirectoryCampaignParser.

        :param file_exploration_strategy: The strategy to apply to interpret the
                                          file hierarchy in terms of experiment
                                          outputs.
        """
        self._file_exploration_strategy = file_exploration_strategy
        self._directories = []

    def parse_file(self, root: str) -> None:
        """
        Explores the file hierarchy rooted at the given directory.

        :param root: The root directory of the file hierarchy to explore.
        """
        self._directories.append(root)
        while self._directories:
            current_dir = self._directories.pop()
            self._file_exploration_strategy.enter_directory(current_dir)
            with scandir(current_dir) as directory:
                self._explore_directory(current_dir, directory)
            self._file_exploration_strategy.exit_directory(current_dir)

    def _explore_directory(self, directory_path: str, directory: Any) -> None:
        """
        Explores the files contained in the given directory.

        :param directory_path: The path of the directory to explore.
        :param directory: The iterator allowing to iterate over the files in the
                          directory.
        """
        for file in directory:
            file_path = path.join(directory_path, file.name)
            if path.isdir(file_path):
                self._directories.append(file_path)
            else:
                self._file_exploration_strategy.parse_file(file_path, file.name)


class FileExplorationStrategy(CampaignParserListenerNotifier):
    """
    The FileExplorationStrategy is the parent class of the strategies that
    allow to interpret a file hierarchy in terms of experiment outputs.
    """

    def __init__(self, listener: CampaignParserListener, configuration: ScalpelConfiguration) -> None:
        """
        Creates a new FileExplorationStrategy.

        :param listener: The listener to notify while parsing.
        :param configuration: The configuration describing the campaign to parse.
        """
        super().__init__(listener, configuration.get_file_name_meta())
        self._configuration = configuration

    def enter_directory(self, directory: str) -> None:
        """
        Notifies this strategy that a directory is entered.
        By default, this method does nothing.

        :param directory: The directory that is entered.
        """
        pass

    def parse_file(self, file_path: str, file_name: str) -> None:
        """
        Asks this strategy to parse a file.

        :param file_path: The path of the file to parse.
        :param file_name: The name of the file to parse.
        """
        raise NotImplementedError('Method "parse_file()" is abstract!')

    def exit_directory(self, directory: str) -> None:
        """
        Notifies this strategy that a directory is exited.
        By default, this method does nothing.

        :param directory: The directory that is exited.
        """
        pass

    def _extract_from_file(self, file_path: str, file_name: str):
        """
        Parses an experiment file of the campaign.

        :param file_path: The path of the file to parse.
        :param file_name: The name of the file to parse.
        """
        if self._configuration.is_to_be_parsed(file_name):
            self.update_file_name_data(file_path)
            parser = self._get_parser_for(file_name, file_path)
            parser.parse()

    def _get_parser_for(self, file_name: str, file_path: str) -> CampaignOutputParser:
        """
        Gives the parser to use to extract data from the given file.

        :param file_name: The name of the file to get the parser for.
        :param file_path: The path of the file to get the parser for.

        :return: The parser to use.
        """
        fmt, config = self._configuration.get_output_format(file_name)

        if fmt == OutputFormat.CSV:
            return CsvCampaignOutputParser(self._listener, file_path, config)

        if fmt == OutputFormat.CSV2:
            return CsvCampaignOutputParser(self._listener, file_path, config)

        if fmt == OutputFormat.TSV:
            return CsvCampaignOutputParser(self._listener, file_path, config)

        if fmt == OutputFormat.JSON:
            return JsonCampaignOutputParser(self._listener, file_path)

        if fmt == OutputFormat.XML:
            return XmlCampaignOutputParser(self._listener, file_path)

        return RawCampaignOutputParser(self._configuration, self._listener, file_path, file_name)


class SingleFileExplorationStrategy(FileExplorationStrategy):
    """
    The SingleFileExplorationStrategy considers that each file encountered
    in a file hierarchy contains the data for exactly one experiment.
    """

    def parse_file(self, file_path: str, file_name: str) -> None:
        """
        Asks this strategy to parse a file.

        :param file_path: The path of the file to parse.
        :param file_name: The name of the file to parse.
        """
        if self._configuration.is_to_be_parsed(file_name):
            self._listener.start_experiment()
            self._extract_from_file(file_path, file_name)
            self.end_experiment()


class NameBasedFileExplorationStrategy(FileExplorationStrategy):
    """
    The NameBasedFileExplorationStrategy considers that the data of an
    experiment is stored in multiple files, having the same name but
    distinct extensions.
    """

    def __init__(self, listener: CampaignParserListener, configuration: ScalpelConfiguration) -> None:
        """
        Creates a new NameBasedFileExplorationStrategy.

        :param listener: The listener to notify while parsing.
        :param configuration: The configuration describing the campaign to parse.
        """
        super().__init__(listener, configuration)
        self._file_names = set()

    def enter_directory(self, directory: str) -> None:
        """
        Notifies this strategy that a directory is entered.
        In this case, the list of files is started to be collected.

        :param directory: The directory that is entered.
        """
        self._file_names = set()

    def parse_file(self, file_path: str, file_name: str) -> None:
        """
        Asks this strategy to parse a file.
        In this case, if the file must be parsed, it is simply kept and
        parsing is delayed.

        :param file_path: The path of the file to parse.
        :param file_name: The name of the file to parse.
        """
        if self._configuration.is_to_be_parsed(file_name):
            self._file_names.add(NameBasedFileExplorationStrategy._file_name_without_extension(file_name))

    def exit_directory(self, directory: str) -> None:
        """
        Notifies this strategy that a directory is exited.
        The files that have been collected are parsed now.

        :param directory: The directory that is exited.
        """
        for file_name in self._file_names:
            self._listener.start_experiment()
            for file in glob(f'{path.join(directory, file_name)}.*'):
                self._extract_from_file(file, basename(file))
            self.end_experiment()

    @staticmethod
    def _file_name_without_extension(file_name: str):
        """
        Removes the extension from the name of a file.

        :param file_name: The name of the file.

        :return: The name of the file, without its extension.
        """
        return splitext(file_name)[0]


class AllFilesExplorationStrategy(FileExplorationStrategy):
    """
    The AllFilesExplorationStrategy considers that all the files contained in
    a given directory contain the data for the same experiment.
    """

    def __init__(self, listener: CampaignParserListener, configuration: ScalpelConfiguration) -> None:
        """
        Creates a new AllFilesExplorationStrategy.

        :param listener: The listener to notify while parsing.
        :param configuration: The configuration describing the campaign to parse.
        """
        super().__init__(listener, configuration)
        self._in_experiment = False

    def parse_file(self, file_path: str, file_name: str) -> None:
        """
        Asks this strategy to parse a file.
        If no experiment has started, invoking this method automatically starts it.

        :param file_path: The path of the file to parse.
        :param file_name: The name of the file to parse.
        """
        if not self._configuration.is_to_be_parsed(file_name):
            return

        if not self._in_experiment:
            # The experiment starts only now to avoid to count empty or
            # intermediate directories as experiments.
            self.start_experiment()
            self._in_experiment = True

        self._extract_from_file(file_path, file_name)

    def exit_directory(self, directory: str) -> None:
        """
        Notifies this strategy that a directory is exited.
        In this case, the current experiment is ended (if any).

        :param directory: The directory that is exited.
        """
        if self._in_experiment:
            self._in_experiment = False
            self.end_experiment()
