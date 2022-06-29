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
This module provides classes for managing the configuration of Scalpel, which
describes how to read the data collected during a campaign.
"""


from __future__ import annotations

from collections import defaultdict
from fnmatch import fnmatch
from os import path, walk
from os import sep as file_separator
from os.path import splitext
from pydoc import locate
from re import escape
from typing import Any, Dict, List, Optional, Type

from metrics.scalpel.config.datafile import DataFile
from metrics.scalpel.config.format import CampaignFormat, InputSetFormat, OutputFormat
from metrics.scalpel.config.inputset import create_input_set_reader
from metrics.scalpel.config.wrapper import IDataFileConfigurationWrapper, \
    IFileNameMetaConfigurationWrapper, IScalpelConfigurationWrapper

from metrics.core.constants import CAMPAIGN_NAME, CAMPAIGN_DATE
from metrics.core.constants import CAMPAIGN_OS, CAMPAIGN_CPU, CAMPAIGN_GPU, CAMPAIGN_MEMORY
from metrics.core.constants import CAMPAIGN_TIMEOUT, CAMPAIGN_MEMOUT
from metrics.core.constants import EXPERIMENT_CPU_TIME
from metrics.core.constants import INPUT_SET_NAME

from metrics.scalpel import CampaignParserListener
from metrics.scalpel.utils import CsvConfiguration
from metrics.scalpel.utils import AbstractExpression, create_filter
from metrics.scalpel.utils import LogData, NullUserDefinedPattern, compile_any
from metrics.scalpel.utils import logger


class FileNameMetaConfiguration:
    """
    The FileNameMetaConfiguration describes how to extract metadata from the
    name of a file.
    """

    def __init__(self, wrapper: IFileNameMetaConfigurationWrapper) -> None:
        """
        Creates a new FileNameMetaConfiguration.

        :param wrapper: The wrapper to create the configuration from.
        """
        self._log_data = FileNameMetaConfiguration._compile(wrapper)

    def get_log_data(self) -> LogData:
        """
        Gives the log-data describing how to extract filename metadata.

        :return: The log-data for the metadata to extract.
        """
        return self._log_data

    def extract_from(self, filename: str) -> Dict[str, str]:
        """
        Extracts the metadata from the given filename.

        :param filename: The name of the file to extract metadata from.

        :return: The extracted data.
        """
        extracted_data = self._log_data.extract_value_from(filename)
        file_name_data = {}
        if extracted_data is not None:
            for name, value in zip(self._log_data.get_names(), extracted_data):
                file_name_data[name] = value
        return file_name_data

    @staticmethod
    def _compile(wrapper: IFileNameMetaConfigurationWrapper) -> LogData:
        """
        Compiles the description of filename metadata into log-data.

        :param wrapper: The wrapper describing filename metadata.

        :return: The compiled log-data.
        """
        # Retrieving the pattern for the metadata, and fixing path separators.
        pattern = wrapper.get_simplified_pattern()
        if pattern is not None:
            pattern = pattern.replace('/', file_separator)

        # Retrieving the regular expression for the metadata, and fixing path separators.
        regex = wrapper.get_regex_pattern()
        if regex is not None:
            regex = regex.replace('/', escape(file_separator))

        if pattern or regex:
            exact = wrapper.is_exact()
            groups = wrapper.get_groups()
            names, indices = zip(*groups)
            compiled_pattern = compile_any(pattern, regex, exact, *indices)
            logger.trace(f'{names} log-data has been compiled to {compiled_pattern}')
            return LogData(names, compiled_pattern)
        return LogData([], NullUserDefinedPattern())


class ScalpelConfigurationLoader:
    """
    The ScalpelConfigurationLoader provides an easy way for loading
    Scalpel's configuration from its wrapper.
    """

    def __init__(self, configuration_wrapper: IScalpelConfigurationWrapper,
                 listener: CampaignParserListener) -> None:
        """
        Creates a new ScalpelConfigurationLoader.

        :param configuration_wrapper: The wrapper for the configuration.
        :param listener: The listener to notify while loading the configuration.
        """
        self._wrapper = configuration_wrapper
        self._listener = listener
        self._path = []
        self._format = None

    def load(self) -> ScalpelConfiguration:
        """
        Loads Scalpel's configuration.

        :return: The loaded configuration.
        """
        self._listener.start_campaign()
        self._load_metadata()
        self._load_experiment_wares()
        self._load_input_set()
        self._load_mapping()
        self._load_default_values()
        self._load_ignored_data()
        return ScalpelConfiguration(self)

    def _load_metadata(self) -> None:
        """
        Loads the metadata of the campaign.
        """
        # Loading data about the campaign itself.
        self._listener.log_data(CAMPAIGN_NAME, self._wrapper.get_campaign_name())
        self._listener.log_data(CAMPAIGN_DATE, self._wrapper.get_campaign_date())

        # Loading the setup of the campaign.
        self._listener.log_data(CAMPAIGN_OS, self._wrapper.get_os_description())
        self._listener.log_data(CAMPAIGN_CPU, self._wrapper.get_cpu_description())
        self._listener.log_data(CAMPAIGN_GPU, self._wrapper.get_gpu_description())
        self._listener.log_data(CAMPAIGN_MEMORY, self._wrapper.get_total_memory())

        # Loading the limits set to the campaign.
        timeout = self._wrapper.get_time_out()
        self._listener.add_default_value(EXPERIMENT_CPU_TIME, timeout)
        self._listener.log_data(CAMPAIGN_TIMEOUT, timeout)
        self._listener.log_data(CAMPAIGN_MEMOUT, self._wrapper.get_memory_out())

    def _load_experiment_wares(self) -> None:
        """
        Loads the description of the experiment-wares used in the campaign.
        """
        for xp_ware in self._wrapper.get_experiment_wares():
            self._listener.start_experiment_ware()
            for key, value in xp_ware.items():
                self._listener.log_data(key, value)
            self._listener.end_experiment_ware()

    def _load_input_set(self) -> None:
        """
        Loads the description of the inputs used in the campaign.
        """
        for input_set in self._wrapper.get_input_set():
            self._listener.start_input_set()
            self._listener.log_data(INPUT_SET_NAME, input_set.get_name())
            fmt = InputSetFormat.value_of(input_set.get_type())
            file_name_meta = FileNameMetaConfiguration(input_set.get_file_name_meta())
            reader = create_input_set_reader(fmt, input_set.get_extensions(), file_name_meta)
            reader(self._listener, input_set.get_files())
            self._listener.end_input_set()

    def _load_mapping(self) -> None:
        """
        Loads the mapping allowing to retrieve the data wanted by Scalpel from
        the experiment files.
        """
        for key, value in self._wrapper.get_mapping().items():
            self._listener.add_key_mapping(key, value)

    def _load_default_values(self) -> None:
        """
        Loads the default values allowing to fix missing values from the
        experiments of the campaign.
        """
        for key, value in self._wrapper.get_default_values().items():
            self._listener.add_default_value(key, value)

    def _load_ignored_data(self) -> None:
        """
        Loads the data that must be ignored when read by Scalpel.
        """
        for data in self._wrapper.get_ignored_data():
            self._listener.add_ignored_data(data)

    def get_campaign_path(self) -> List[str]:
        """
        Gives the path of the files containing all the data about the campaign.
        These files may be either regular files or directories.

        :return: The path to the main files of the campaign.
        """
        self._path = self._wrapper.get_campaign_path()
        return self._path

    def get_format(self) -> CampaignFormat:
        """
        Gives the format of the campaign to parse.

        :return: The format of the campaign to parse.

        :raises ValueError: If the format is unspecified and could not be guessed.
        """
        # If the user has specified a format, we use it.
        fmt = self._wrapper.get_format()
        if fmt is not None:
            self._format = CampaignFormat.value_of(fmt)
            logger.trace(f'campaign parsed using the {self._format} strategy')
            return self._format

        # Otherwise, we try to guess the format.
        self._format = self._guess_format()
        if self._format is None:
            raise ValueError('Could not infer campaign format')

        # Returning the guessed format.
        logger.trace(f'campaign parsed using the {self._format} strategy')
        return self._format

    def _guess_format(self) -> Optional[CampaignFormat]:
        """
        Guesses the format of the campaign to parse.

        :return: The guessed format of the campaign, or None if it could not be guessed.
        """
        if path.isdir(self._path[0]):
            return self._guess_directory_format()
        if path.exists(self._path[0]):
            return self._guess_regular_format()
        return None

    def _guess_directory_format(self) -> Optional[CampaignFormat]:
        """
        Guesses the format of the campaign to parse when stored in a directory.

        :return: The format of the campaign, guessed from the deepness of the
                 file hierarchy rooted at the first main file of this campaign.
        """
        for _, dirs, _ in walk(self._path[0]):
            if dirs:
                return CampaignFormat.EXPERIMENT_DIRECTORY
        return CampaignFormat.SINGLE_EXPERIMENT_LOG_FILE

    def _guess_regular_format(self) -> Optional[CampaignFormat]:
        """
        Guesses the format of the campaign to parse when stored in a regular file.

        :return: The format of the campaign, guessed from the extension of its first
                 main file, or None if it could not be guessed.
        """
        ext = splitext(self._path[0])[1]
        return CampaignFormat.value_of(ext[1:])

    def get_csv_configuration(self) -> Optional[CsvConfiguration]:
        """
        Gives the CSV configuration describing the CSV format used by
        the files of the campaign to parse.

        :return: The CSV configuration of the files of the campaign.
                 The result is None if the files are not CSV files.
        """
        if not self._format.is_csv() and not self._format.is_reverse_csv():
            # The campaign is not in a CSV format, so there is no configuration.
            return None

        return CsvConfiguration(has_header=self.has_header(),
                                quote_char=self.get_quote_char(),
                                separator=self.get_separator(),
                                title_separator=self.get_title_separator())

    def get_separator(self) -> str:
        """
        Gives the separator used to distinguish different fields in the files to parse.

        :return: The separator that is used (if specified).
        """
        sep = self._wrapper.get_separator()
        if sep is not None:
            return sep
        if self._format == CampaignFormat.CSV2:
            return ';'
        if self._format == CampaignFormat.TSV:
            return '\t'
        return ','

    def get_title_separator(self) -> str:
        """
        Gives the separator used to distinguish different elements in the titles of
        the files to parse.

        :return: The title separator that is used.
        """
        sep = self._wrapper.get_title_separator()
        if sep is None:
            return '.'
        return sep

    def get_custom_parser(self) -> Optional[Type]:
        """
        Gives the custom parser to use to parse the campaign.

        :return: The parser for the campaign (if specified).

        :raises ValueError: If the specified parser is not a valid type.
        """
        parser_class = self._wrapper.get_custom_parser()
        return ScalpelConfigurationLoader._load_class(parser_class)

    def get_is_success(self) -> AbstractExpression:
        """
        Gives the expression to use to validate an experiment as a success.

        :return: The expression to use to determine whether an experiment is successful.
        """
        expr = self._wrapper.get_is_success()
        return create_filter(expr)

    def get_file_name_meta(self) -> FileNameMetaConfiguration:
        """
        Gives the description of the metadata to extract from the name of the
        files of the campaign.

        :return: The configuration for extracting metadata.
        """
        return FileNameMetaConfiguration(self._wrapper.get_file_name_meta())

    def get_log_datas(self) -> Dict[Optional[str], List[LogData]]:
        """
        Gives the description of the log-data to extract from raw campaign files.

        :return: The log-data describing how to extract relevant data.
        """
        log_data = defaultdict(list)
        for data in self._wrapper.get_raw_data():
            file = data.get_file()
            pattern = data.get_simplified_pattern()
            regex = data.get_regex_pattern()
            exact = data.is_exact()
            names, groups = zip(*data.get_groups())
            compiled_pattern = compile_any(pattern, regex, exact, *groups)
            logger.trace(f'{names} log-data has been compiled to {compiled_pattern}')
            log_data[file].append(LogData(names, compiled_pattern))
        return log_data

    def get_data_files(self) -> Dict[str, DataFile]:
        """
        Gives the description of the data-files from which to extract campaign data.

        :return: The data-files of the campaign.
        """
        data_files = {}
        for data_file in self._wrapper.get_data_files():
            name = data_file.get_name()
            prefix = data_file.has_name_as_prefix()

            fmt = data_file.get_format()
            if fmt is None:
                output_fmt = OutputFormat.guess_format(name)
            else:
                output_fmt = OutputFormat.value_of(fmt)

            config = None
            if output_fmt.is_csv():
                sep = ScalpelConfigurationLoader._guess_data_file_separator(data_file, output_fmt)
                config = CsvConfiguration(has_header=data_file.has_header(),
                                          quote_char=data_file.get_quote_char(),
                                          separator=sep)

            parser = data_file.get_custom_parser()
            data_files[name] = DataFile(name, prefix, output_fmt, config, parser)
        return data_files

    @staticmethod
    def _guess_data_file_separator(data_file: IDataFileConfigurationWrapper,
                                   fmt: OutputFormat) -> str:
        """
        Guesses the separator for a CSV data-file.

        :param data_file: The data-file to guess the separator of.
        :param fmt: The format of the data-file.

        :return: The guessed separator of the data-file.
        """
        sep = data_file.get_separator()
        if sep is not None:
            return sep
        if fmt == OutputFormat.CSV2:
            return ';'
        if fmt == OutputFormat.TSV:
            return '\t'
        return ','

    @staticmethod
    def _load_class(class_name: Optional[str]) -> Optional[Type]:
        """
        Loads a class from its name.

        :param class_name: The name of the class to load.

        :return: The loaded class.

        :raises ValueError: If the class cannot be loaded.
        """
        # Checking if there is a class to load.
        if class_name is None:
            return None

        # Looking for the class.
        class_object = locate(class_name)
        if isinstance(class_object, type):
            return class_object

        # The class could not be found.
        raise ValueError(f'Could not find class "{class_name}"')

    def __getattr__(self, item: str) -> Any:
        """
        Delegates the access to attributes to the wrapper.

        :param item: The name of the attribute to access to.

        :return: The accessed attribute.
        """
        return getattr(self._wrapper, item)


class ScalpelConfiguration:
    """
    The ScalpelConfiguration describes how relevant values may be retrieved from the
    files of a campaign.
    """

    def __init__(self, loader: ScalpelConfigurationLoader) -> None:
        """
        Creates a new ScalpelConfiguration.

        :param loader: The loader from which to load the configuration.
        """
        self._path = loader.get_campaign_path()
        self._format = loader.get_format()
        self._csv_configuration = loader.get_csv_configuration()
        self._follow_symlinks = loader.get_follow_symlinks()
        self._custom_parser = loader.get_custom_parser()
        self._is_success = loader.get_is_success()
        self._file_name_meta = loader.get_file_name_meta()
        self._log_datas = loader.get_log_datas()
        self._data_files = loader.get_data_files()
        self._ignored_files = loader.get_ignored_files()

    def get_path(self) -> List[str]:
        """
        Gives the list of the paths of main files of the campaign, from which
        to start extracting relevant values.

        :return: The paths of the main files of the campaign.
        """
        return self._path

    def get_format(self) -> CampaignFormat:
        """
        Gives the format of the campaign to parse.

        :return: The format of the campaign.
        """
        return self._format

    def get_csv_configuration(self) -> Optional[CsvConfiguration]:
        """
        Gives the CSV configuration describing the CSV format used by
        the files of the campaign to parse.

        :return: The CSV configuration of the files of the campaign.
                 The result is None when the files are not CSV files.
        """
        return self._csv_configuration

    def get_follow_symlinks(self):
        """
        Checks whether symbolic links should be followed when exploring a file hierarchy.

        :return: Whether symlinks should be followed.
        """
        return self._follow_symlinks

    def get_custom_parser(self) -> Optional[Type]:
        """
        Gives the custom parser to use to parse the campaign.

        :return: The class of the parser for the campaign (if specified).
        """
        return self._custom_parser

    def get_is_success(self) -> AbstractExpression:
        """
        Gives the expression to use to validate an experiment as a success.

        :return: The expression to use to determine whether an experiment is successful.
        """
        return self._is_success

    def get_file_name_meta(self) -> FileNameMetaConfiguration:
        """
        Gives the configuration for the metadata to extract from the name of the
        files of the campaign.

        :return: The configuration of the metadata.
        """
        return self._file_name_meta

    def is_to_be_parsed(self, filename: str) -> bool:
        """
        Checks whether the given file must be parsed by Scalpel.

        :param filename: The name of the file to check.

        :return: Whether the file must be parsed.
        """
        if any(fnmatch(filename, ignored_file) for ignored_file in self._ignored_files):
            return False

        if any(fnmatch(filename, data_file) for data_file in self._log_datas):
            return True

        if any(fnmatch(filename, data_file) for data_file in self._data_files):
            return True

        return False

    def get_data_in(self, filename: str) -> List[LogData]:
        """
        Gives the data to retrieve from the given file.

        :param filename: The name of the file from which to extract data.

        :return: The description of the data to extract from the file.
        """
        if None in self._log_datas:
            return self._log_datas[None]

        all_datas = []
        for file, log_data in self._log_datas.items():
            if fnmatch(filename, file):
                all_datas.extend(log_data)
        return all_datas

    def get_data_file(self, name: str) -> Optional[DataFile]:
        """
        Gives the data-file whose name matches the given one.

        :param name: The name of the data-file to look for.

        :return: The data-file with the given name, or None if no such data-file exist.
        """
        for file, data_file in self._data_files.items():
            if fnmatch(name, file):
                return data_file
        return None
