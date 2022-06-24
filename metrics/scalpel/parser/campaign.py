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
This module provides various classes for parsing different types of files containing
the results of a campaign, to build the representation of this campaign.
"""


from __future__ import annotations

from collections import defaultdict
from glob import glob
from os import path, walk
from os.path import basename, splitext
from typing import Any, Dict, Generator, List, Optional, TextIO, Tuple

from metrics.core.constants import EXPERIMENT_CPU_TIME, EXPERIMENT_INPUT, EXPERIMENT_XP_WARE

from metrics.scalpel.parser.output import CampaignOutputParser
from metrics.scalpel.parser.output import CsvCampaignOutputParser
from metrics.scalpel.parser.output import JsonCampaignOutputParser, XmlCampaignOutputParser
from metrics.scalpel.parser.output import RawCampaignOutputParser

from metrics.scalpel import CampaignParserListener
from metrics.scalpel.config import FileNameMetaConfiguration, OutputFormat, ScalpelConfiguration

from metrics.scalpel.utils import CsvConfiguration, CsvReader
from metrics.scalpel.utils import logger, timeit


class CampaignParserListenerNotifier:
    """
    The CampaignParserListenerNotifier is "trait" class allowing to easily notify
    a CampaignParserListener about parsing events, whatever how parsing is achieved.
    """

    def __init__(self, listener: CampaignParserListener,
                 file_name_meta: FileNameMetaConfiguration) -> None:
        """
        Creates a new CampaignParserListenerNotifier.

        :param listener: The listener to notify while parsing.
        :param file_name_meta: The configuration object describing how to extract
                               metadata from the path of the parsed files.
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
        if extracted_data:
            logger.trace(f'data {extracted_data} extracted from path "{file}"')
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

    @timeit
    def parse_file(self, file_path: str) -> None:
        """
        Parses the file at the given path to extract data about the campaign.

        :param file_path: The path of the file to read.
        """
        logger.info(f'extracting data from regular file "{file_path}"...')
        self.update_file_name_data(file_path)
        with open(file_path, 'r', encoding='utf-8') as file:
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
        :param file_name_meta: The configuration object describing how to extract
                               metadata from the path of the parsed file.
        :param csv_configuration: The configuration for the CSV reader.
        """
        super().__init__(listener, file_name_meta)
        self._csv_configuration = csv_configuration
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

        :return: The header of the CSV stream.
        """
        self._reader = CsvReader(stream, self._csv_configuration, self._row_filter)
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
        Checks whether the given row is relevant for the purpose of the campaign.

        :param row: The row to check.

        :return: Whether the given row is relevant.
        """
        return True


class ReverseCsvCampaignParser(CsvCampaignParser):
    """
    The ReverseCsvCampaignParser is a parser that allows to parse a CSV file
    in which each line corresponds to an input, and the columns to the values
    collected for different experiment-wares on the corresponding input.
    """

    def __init__(self, listener: CampaignParserListener, file_name_meta: FileNameMetaConfiguration,
                 csv_configuration: CsvConfiguration) -> None:
        """
        Creates a new ReverseCsvCampaignParser.

        :param listener: The listener to notify while parsing.
        :param file_name_meta: The configuration object describing how to extract
                               metadata from the path of the parsed file.
        :param csv_configuration: The configuration for the CSV reader.
        """
        super().__init__(listener, file_name_meta, csv_configuration)
        self._input_mapping = listener.get_mapping(EXPERIMENT_INPUT)
        self._experiment_wares = set()
        self._data_names = set()
        self._current_input = 0

    def parse_header(self, stream: TextIO) -> List[str]:
        """
        Parses the header of a CSV stream.

        :param stream: The stream to read.

        :return: The data available in the CSV stream.
        """
        header = []

        # Extracting the experiment-wares and the statistics to collect.
        for key in super().parse_header(stream):
            if key in self._input_mapping:
                header.append(key)
            else:
                split_key = key.split(self._csv_configuration.get_title_separator(), 1)
                self._experiment_wares.add(split_key[0])
                self._data_names.add('' if len(split_key) == 1 else split_key[1])

        header.extend(self._data_names)
        logger.trace(f'keys {header} adapted from CSV header')
        return header

    def parse_content(self) -> None:
        """
        Parses the content of a CSV stream using the associated reader.
        This reader must have been initialized using "parse_header()" before
        invoking this method.
        """
        for line in self._reader.read_content():
            line_data = dict(line)
            input_data = self._extract_input_data(line_data)
            for xp_ware in self._experiment_wares:
                self.start_experiment()
                self._log_experiment(xp_ware, input_data, line_data)
                self.end_experiment()

    def _extract_input_data(self, line: Dict[str, str]) -> Dict[str, str]:
        """
        Extracts the data corresponding to an input from the given line.

        :param line: The line to extract data from.

        :return: The data corresponding to the input.
        """
        if len(self._input_mapping) == 1 and self._input_mapping[0] not in line:
            # There is no data about the input in the line.
            self._current_input += 1
            return {EXPERIMENT_INPUT: f'unknown input #{self._current_input}'}

        # Collecting the data about the input.
        return {key: line[key] for key in self._input_mapping}

    def _log_experiment(self, experiment_ware: str, input_data: Dict[str, str],
                        line: Dict[str, str]) -> None:
        """
        Logs data about an experiment.

        :param experiment_ware: The experiment-ware used for the experiment.
        :param input_data: The data about the input used for the experiment.
        :param line: All the data about the experiment.
        """
        # Logging the name of the experiment-ware.
        self.log_data(EXPERIMENT_XP_WARE, experiment_ware)

        # Logging data about the input.
        for key, value in input_data.items():
            self.log_data(key, value)

        # Logging statistics about the experiment.
        for data in self._data_names:
            if data == '':
                self.log_data(EXPERIMENT_CPU_TIME, line[experiment_ware])
            else:
                self.log_data(data, line[f'{experiment_ware}.{data}'])


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
        :param file_name_meta: The configuration object describing how to extract
                               metadata from the path of the file to parse.
        """
        super().__init__(listener, file_name_meta, CsvConfiguration(separator='|'))

    def _row_filter(self, row: List[str]) -> bool:
        """
        Checks whether the given row is relevant for the purpose of the campaign.

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

    def __init__(self, configuration: ScalpelConfiguration,
                 file_exploration_strategy: FileExplorationStrategy) -> None:
        """
        Creates a new DirectoryCampaignParser.

        :param configuration: The configuration describing the campaign to parse.
        :param file_exploration_strategy: The strategy to apply to interpret the file
                                          hierarchy in terms of experiment outputs.
        """
        self._configuration = configuration
        self._file_exploration_strategy = file_exploration_strategy
        self._directories = None

    @timeit
    def parse_file(self, file_path: str) -> None:
        """
        Explores the file hierarchy rooted at the given directory.

        :param file_path: The root directory of the file hierarchy to explore.
        """
        logger.info(f'extracting data from directory "{file_path}"...')
        self._directories = defaultdict(list)
        self._find_relevant_files(file_path)
        self._parse_relevant_files()

    def _find_relevant_files(self, root: str):
        """
        Finds the relevant files in the file hierarchy of the campaign.

        :param root: The root of the file hierarchy to explore.
        """
        for file in self._find(root):
            xp_dir, xp_file = self._extract_relevant_file(file)
            if xp_file is not None:
                self._directories[xp_dir].append(xp_file)

    def _extract_relevant_file(self, file_path: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extracts a relevant file from the given path.
        To this end, all possible relative paths are compared to those described in the
        configuration to check whether the file is to be parsed.

        :param file_path: The path of the file to extract a file from.

        :return: The path of the directory containing the relevant file and the path of the
                 relevant file inside this directory, or (None, None) if the file is not
                 relevant.
        """
        split = file_path.split(path.sep)
        for i in range(len(split) - 1, -1, -1):
            directory = path.join(split[0], *split[1:i]) if i > 0 else '.'
            file = path.join(split[i], *split[i+1:]) if i < len(split) - 1 else split[i]
            if self._configuration.is_to_be_parsed(file):
                logger.trace(f'relevant file found at "{file_path}"')
                return directory, file
        logger.trace(f'ignored file at "{file_path}"')
        return None, None

    def _parse_relevant_files(self) -> None:
        """
        Parses the relevant files that have been found in the file hierarchy of the campaign.
        """
        for directory, files in self._directories.items():
            self._file_exploration_strategy.enter_directory(directory)
            for file in files:
                file_path = path.join(directory, file)
                self._file_exploration_strategy.parse_file(file_path, file)
            self._file_exploration_strategy.exit_directory(directory)

    def _find(self, root: str) -> Generator[str]:
        """
        Finds all regular files in the file hierarchy rooted at the given directory.

        :param root: The root directory of the file hierarchy to explore.

        :return: A generator of the regular files in the hierarchy.
        """
        for folder, _, files in walk(root, followlinks=self._configuration.get_follow_symlinks()):
            for file in files:
                yield path.join(folder, file)


class FileExplorationStrategy(CampaignParserListenerNotifier):
    """
    The FileExplorationStrategy is the parent class of the strategies that
    allow to interpret a file hierarchy in terms of experiment outputs.
    """

    def __init__(self, listener: CampaignParserListener,
                 configuration: ScalpelConfiguration) -> None:
        """
        Creates a new FileExplorationStrategy.

        :param listener: The listener to notify while parsing.
        :param configuration: The configuration describing the campaign to parse.
        """
        super().__init__(listener, configuration.get_file_name_meta())
        self._configuration = configuration

    def end_experiment(self) -> None:
        """
        Notifies the listener that the current experiment has been fully parsed.
        """
        super().end_experiment()
        super().reset_file_name_data()

    def enter_directory(self, directory: str) -> None:
        """
        Notifies this strategy that a directory is entered.
        By default, this method does nothing.

        :param directory: The directory that is entered.
        """

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
        It is supposed that the file has indeed to be parsed.

        :param file_name: The name of the file to get the parser for.
        :param file_path: The path of the file to get the parser for.

        :return: The parser to use.
        """
        data_file = self._configuration.get_data_file(file_name)

        # By default, a raw parser is used.
        if data_file is None:
            logger.trace(f'raw parser used for "{file_path}"')
            return RawCampaignOutputParser(self._listener, file_path, file_name,
                                           False, self._configuration)

        # Looking for a user-implemented parser.
        parser = data_file.get_custom_parser()
        if parser is not None:
            logger.trace(f'custom parser {parser} used for "{file_path}"')
            return parser(self._listener, self._configuration, file_path, file_name)

        # Using the most appropriate parser, based on the format of the file.
        fmt = data_file.get_format()

        if fmt.is_csv():
            logger.trace(f'CSV parser used for "{file_path}"')
            return CsvCampaignOutputParser(self._listener, file_path, file_name,
                                           data_file.has_name_as_prefix(),
                                           data_file.get_csv_configuration())

        if fmt == OutputFormat.JSON:
            logger.trace(f'JSON parser used for "{file_path}"')
            return JsonCampaignOutputParser(self._listener, file_path, file_name,
                                            data_file.has_name_as_prefix())

        if fmt == OutputFormat.XML:
            logger.trace(f'XML parser used for "{file_path}"')
            return XmlCampaignOutputParser(self._listener, file_path, file_name,
                                           data_file.has_name_as_prefix())

        logger.trace(f'raw parser used for "{file_path}"')
        return RawCampaignOutputParser(self._listener, file_path, file_name,
                                       data_file.has_name_as_prefix(), self._configuration)


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
            self.start_experiment()
            logger.debug(f'extracting data from regular file "{file_path}"...')
            self._extract_from_file(file_path, file_name)
            self.end_experiment()


class NameBasedFileExplorationStrategy(FileExplorationStrategy):
    """
    The NameBasedFileExplorationStrategy considers that the data of an
    experiment is stored in multiple files, having the same name but
    distinct extensions.
    """

    def __init__(self, listener: CampaignParserListener,
                 configuration: ScalpelConfiguration) -> None:
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
            name = NameBasedFileExplorationStrategy._file_name_without_extension(file_name)
            logger.trace(f'name "{name}" detected as an experiment identifier')
            self._file_names.add(name)

    def exit_directory(self, directory: str) -> None:
        """
        Notifies this strategy that a directory is exited.
        The files that have been collected are parsed now.

        :param directory: The directory that is exited.
        """
        for file_name in self._file_names:
            self._listener.start_experiment()
            for file in glob(f'{path.join(directory, file_name)}.*'):
                logger.debug(f'extracting data from regular file "{file}"...')
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

    def __init__(self, listener: CampaignParserListener,
                 configuration: ScalpelConfiguration) -> None:
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
            logger.trace(f'ignoring file "{file_path}"')
            return

        if not self._in_experiment:
            # The experiment starts only now to avoid considering empty or
            # intermediate directories as experiments.
            self.start_experiment()
            self._in_experiment = True

        logger.debug(f'extracting data from regular file "{file_path}"...')
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
