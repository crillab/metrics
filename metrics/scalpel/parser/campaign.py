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


from glob import glob
from os import path, scandir
from os.path import splitext
from typing import Any, Dict, List, Set, TextIO

from metrics.core.constants import EXPERIMENT_XP_WARE
from metrics.scalpel.config import ScalpelConfiguration
from metrics.scalpel.config.config import FileNameMetaConfiguration, CsvConfiguration
from metrics.scalpel.config.format import OutputFormat
from metrics.scalpel.listener import CampaignParserListener
from metrics.scalpel.parser.output import CampaignOutputParser, \
    CsvCampaignOutputParser, JsonCampaignOutputParser, XmlCampaignOutputParser, \
    RawCampaignOutputParser
from metrics.scalpel.parser.utils import CsvReader


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
        self._listener.end_experiment()


class FileCampaignParser(CampaignParser):
    """
    The FileCampaignParser is the parent class of all the parsers allowing to
    read the results of a campaign from a (regular) file.
    """

    def __init__(self, listener: CampaignParserListener, file_name_meta: FileNameMetaConfiguration) -> None:
        """
        Creates a new FileCampaignParser.

        :param listener: The listener to notify while parsing.
        :param file_name_meta: The configuration object describing how to
                               extract metadata from the path of the file to
                               parse.
        """
        super().__init__(listener)
        self._file_name_meta = file_name_meta
        self._file_name_data = None

    def end_experiment(self) -> None:
        """
        Notifies the listener that the current experiment has been fully parsed,
        after having logged metadata extracted from the name of the file that
        is being parsed.
        """
        for key, value in self._file_name_data.items():
            self.log_data(key, value)
        super().end_experiment()

    def parse_file(self, file_path: str) -> None:
        """
        Parses the file at the given path to extract data about the campaign.

        :param file_path: The path of the file to read.
        """
        self._file_name_data = self._extract_file_name_meta(file_path)
        with open(file_path, 'r') as file:
            self.parse_stream(file)
        self._file_name_data = None

    def _extract_file_name_meta(self, file_path: str) -> Dict[str, Any]:
        """
        Extracts metadata from the path of the file to parse.

        :param file_path: The path of the file to extract metadata from.

        :return: The extracted metadata.
        """
        log_data = self._file_name_meta.get_log_data()
        extracted_data = log_data.extract_value_from(file_path)

        file_name_data = {}
        if extracted_data is not None:
            for name, value in zip(log_data.get_names(), extracted_data):
                file_name_data[name] = value
        return file_name_data

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

    def __init__(self, listener: CampaignParserListener, csv_configuration: CsvConfiguration,
                 file_name_meta: FileNameMetaConfiguration) -> None:
        """
        Creates a new CsvCampaignParser.

        :param listener: The listener to notify while parsing.
        :param csv_configuration: The configuration for the CSV reader.
        :param file_name_meta: The configuration object describing how to
                               extract metadata from the path of the file to
                               parse.
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
        Parses the content of a CSV stream using the given reader.
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
        super().__init__(listener, CsvConfiguration('|'), file_name_meta)

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
    The DirectoryCampaignParser explores a file hierarchy containing all the
    output files produced during a campaign.
    """

    def __init__(self, configuration: ScalpelConfiguration,
                 listener: CampaignParserListener) -> None:
        """
        Creates a new DirectoryCampaignParser.

        :param configuration: The configuration describing how to extract
                              data from the output files.
        :param listener: The listener to notify while parsing.
        """
        super().__init__(listener)
        self._configuration = configuration
        self._file_name_data = {}

    def end_experiment(self) -> None:
        """
        Notifies the listener that the current experiment has been fully parsed,
        after having logged metadata extracted from the name of the file that
        is being parsed.
        """
        for key, value in self._file_name_data.items():
            self.log_data(key, value)
        self._file_name_data = {}
        super().end_experiment()

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

    def _extract_file_name_meta(self, file_path: str) -> None:
        """
        Extracts metadata from the path of the file to parse.

        :param file_path: The path of the file to extract metadata from.
        """
        log_data = self._configuration.get_file_name_meta().get_log_data()
        extracted_data = log_data.extract_value_from(file_path)

        self._file_name_data = {}
        if extracted_data is not None:
            for name, value in zip(log_data.get_names(), extracted_data):
                self._file_name_data[name] = value

    def _get_parser_for(self, file_name: str, file_path: str) -> CampaignOutputParser:
        """
        Gives the parser to use to extract data from the given file.

        :param file_name: The name of the file to get the parser for.
        :param file_path: The path of the file to get the parser for.

        :return: The parser to use.
        """
        fmt = DirectoryCampaignParser._guess_format(file_name)

        if fmt == OutputFormat.CSV:
            return CsvCampaignOutputParser(self._listener, file_path)

        if fmt == OutputFormat.CSV2:
            return CsvCampaignOutputParser(self._listener, file_path, CsvConfiguration(';'))

        if fmt == OutputFormat.TSV:
            return CsvCampaignOutputParser(self._listener, file_path, CsvConfiguration('\t'))

        if fmt == OutputFormat.JSON:
            return JsonCampaignOutputParser(self._listener, file_path)

        if fmt == OutputFormat.XML:
            return XmlCampaignOutputParser(self._listener, file_path)

        return RawCampaignOutputParser(self._configuration, self._listener, file_path, file_name)

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
                 listener: CampaignParserListener) -> None:
        """
        Creates a new DeepDirectoryCampaignParser.

        :param configuration: The configuration describing how to extract
                              data from the output files.
        :param listener: The listener to notify while parsing.
        """
        super().__init__(configuration, listener)
        self._depth = configuration.get_hierarchy_depth()
        self._experiment_ware_depth = configuration.get_experiment_ware_depth()
        self._experiment_ware = None

    def explore(self, root: str) -> None:
        """
        Explores the file hierarchy rooted at the given directory.

        :param root: The root directory of the file hierarchy to explore.
        """
        self.recursive_explore(root)

    def recursive_explore(self, directory: str, depth: int = 0) -> None:
        """
        Recursively explores the file hierarchy rooted at the given directory.

        :param directory: The directory to explore.
        :param depth: The depth of the directory that is being explored
                      (w.r.t. the root directory).
        """
        if not path.isdir(directory):
            return

        if depth == self._experiment_ware_depth:
            self._experiment_ware = path.basename(directory)

        if depth == self._depth:
            self._explore_experiment(directory)

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
            if self._experiment_ware is not None:
                self.log_data(EXPERIMENT_XP_WARE, self._experiment_ware)
            for file in experiment:
                if self._configuration.is_to_be_parsed(file.name):
                    self._parse_file(directory, file.name)
            self.end_experiment()

    def _parse_file(self, directory: str, file_name: str) -> None:
        """
        Parses an output file of the campaign.

        :param directory: The directory of the experiment being considered.
        :param file_name: The name of the file to consider.
        """
        file_path = path.join(directory, file_name)
        self._extract_file_name_meta(file_path)
        parser = self._get_parser_for(file_name, file_path)
        parser.parse()


class FlatDirectoryCampaignParser(DirectoryCampaignParser):
    """
    The FlatDirectoryCampaignParser allows to extract data collected during
    a campaign when they are stored in a single directory, in which all files
    correspond to exactly one experiment.
    """

    def explore(self, root: str) -> None:
        """
        Explores the file hierarchy rooted at the given directory.

        :param root: The root directory of the file hierarchy to explore.
        """
        with scandir(root) as root_dir:
            for file in root_dir:
                self.start_experiment()
                self._parse_file(root, file.name)
                self.end_experiment()

    def _parse_file(self, root: str, file_name: str):
        """
        Parses an experiment file of the campaign.

        :param root: The root directory of the campaign.
        :param file_name: The name of the file to consider.
        """
        self._extract_file_name_meta(file_name)
        file_path = path.join(root, file_name)
        parser = self._get_parser_for(file_name, file_path)
        parser.parse()


class FlatDirectoryMultipleFilesCampaignParser(DirectoryCampaignParser):
    """
    The FlatDirectoryMultipleFilesCampaignParser allows to extract the data
    collected during a campaign when they are stored in a single directory,
    in which all files with the same name (but different extensions) correspond
    to exactly one experiment.
    """

    def explore(self, root: str) -> None:
        """
        Explores the file hierarchy rooted at the given directory.

        :param root: The root directory of the file hierarchy to explore.
        """
        for file_name in self._find_names(root):
            self._parse_files(root, file_name)

    def _find_names(self, root: str) -> Set[str]:
        """
        Collects the names (without extension) of the relevant files that are
        stored in the given directory.

        :param root: The root directory of the file hierarchy to explore.

        :return: The set of the file names in the root directory.
        """
        with scandir(root) as root_dir:
            names = set()
            for file in root_dir:
                if self._configuration.is_to_be_parsed(file.name):
                    names.add(self._file_name_without_extension(file.name))
            return names

    def _parse_files(self, root: str, file_name: str) -> None:
        """
        Parses the file with the given name in the given directory.

        :param root: The root directory of the campaign.
        :param file_name: The name (without extension) of the files to parse.
        """
        self.start_experiment()
        self._extract_file_name_meta(file_name)
        for file in glob(f'{path.join(root, file_name)}.*'):
            if self._configuration.is_to_be_parsed(file):
                parser = self._get_parser_for(file, file)
                parser.parse()
        self.end_experiment()

    @staticmethod
    def _file_name_without_extension(file_name: str):
        """
        Removes the extension from the name of a file.

        :param file_name: The name of the file.

        :return: The name of the file, without its extension.
        """
        return splitext(file_name)[0]


class FileExplorationStrategy:

    def __init__(self, listener: CampaignParserListener, configuration: ScalpelConfiguration) -> None:
        self._listener = listener
        self._configuration = configuration

    def enter_directory(self, directory):
        raise NotImplementedError

    def parse_file(self, file_path, file_name):
        raise NotImplementedError

    def exit_directory(self, directory):
        raise NotImplementedError

    def _extract_file_name_meta(self, file_path: str) -> None:
        """
        Extracts metadata from the path of the file to parse.

        :param file_path: The path of the file to extract metadata from.
        """
        log_data = self._configuration.get_file_name_meta().get_log_data()
        extracted_data = log_data.extract_value_from(file_path)

        if extracted_data is not None:
            for name, value in zip(log_data.get_names(), extracted_data):
                self._listener.log_data(name, value)

    def _get_parser_for(self, file_name: str, file_path: str) -> CampaignOutputParser:
        """
        Gives the parser to use to extract data from the given file.

        :param file_name: The name of the file to get the parser for.
        :param file_path: The path of the file to get the parser for.

        :return: The parser to use.
        """
        fmt = self._guess_format(file_name)

        if fmt == OutputFormat.CSV:
            return CsvCampaignOutputParser(self._listener, file_path)

        if fmt == OutputFormat.CSV2:
            return CsvCampaignOutputParser(self._listener, file_path, CsvConfiguration(';'))

        if fmt == OutputFormat.TSV:
            return CsvCampaignOutputParser(self._listener, file_path, CsvConfiguration('\t'))

        if fmt == OutputFormat.JSON:
            return JsonCampaignOutputParser(self._listener, file_path)

        if fmt == OutputFormat.XML:
            return XmlCampaignOutputParser(self._listener, file_path)

        return RawCampaignOutputParser(self._configuration, self._listener, file_path, file_name)

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


class SingleFileExplorationStrategy(FileExplorationStrategy):

    def enter_directory(self, directory):
        pass

    def parse_file(self, file_path, file_name):
        self._listener.start_experiment()
        self._extract_file_name_meta(file_name)
        parser = self._get_parser_for(file_name, file_path)
        parser.parse()
        self._listener.end_experiment()

    def exit_directory(self, directory):
        pass


class NameBasedFileExplorationStrategy(FileExplorationStrategy):

    def __init__(self, listener: CampaignParserListener, configuration: ScalpelConfiguration) -> None:
        super().__init__(listener, configuration)
        self._file_names = set()

    def enter_directory(self, directory):
        self._file_names = set()

    def parse_file(self, file_path, file_name):
        if self._configuration.is_to_be_parsed(file_name):
            self._file_names.add(self._file_name_without_extension(file_name))

    def exit_directory(self, directory):
        for file_name in self._file_names:
            self._listener.start_experiment()
            self._extract_file_name_meta(file_name)
            for file in glob(f'{path.join(directory, file_name)}.*'):
                if self._configuration.is_to_be_parsed(file):
                    parser = self._get_parser_for(file, file)
                    parser.parse()
            self._listener.end_experiment()

    @staticmethod
    def _file_name_without_extension(file_name: str):
        """
        Removes the extension from the name of a file.

        :param file_name: The name of the file.

        :return: The name of the file, without its extension.
        """
        return splitext(file_name)[0]


class AllFilesExplorationStrategy(FileExplorationStrategy):

    def enter_directory(self, directory):
        self._listener.start_experiment()

    def parse_file(self, file_path, file_name):
        if self._configuration.is_to_be_parsed(file_name):
            self._extract_file_name_meta(file_path)
            parser = self._get_parser_for(file_name, file_path)
            parser.parse()

    def exit_directory(self, directory):
        self._listener.end_experiment()


class DynamicHierarchyCampaignParser(DirectoryCampaignParser):

    def __init__(self, configuration: ScalpelConfiguration,
                 listener: CampaignParserListener,
                 file_exploration_strategy: FileExplorationStrategy) -> None:
        """
        Creates a new DeepDirectoryCampaignParser.

        :param configuration: The configuration describing how to extract
                              data from the output files.
        :param listener: The listener to notify while parsing.
        """
        super().__init__(configuration, listener)
        self._file_exploration_strategy = file_exploration_strategy
        self._directories = []

    def explore(self, root: str) -> None:
        """
        Explores the file hierarchy rooted at the given directory.

        :param root: The root directory of the file hierarchy to explore.
        """
        self._directories.append(root)
        while self._directories:
            current_dir = self._directories.pop()
            self._file_exploration_strategy.enter_directory(current_dir)
            with scandir(current_dir) as directory:
                self.explore_directory(current_dir, directory)
            self._file_exploration_strategy.exit_directory(current_dir)

    def explore_directory(self, current_dir, directory):
        for file in directory:
            file_path = path.join(current_dir, file.name)
            if path.isdir(file_path):
                self._directories.append(file_path)
            else:
                self._file_exploration_strategy.parse_file(file_path, file.name)
