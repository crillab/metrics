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
This module provides classes for managing the configuration of Scalpel, which
describes how to read the data collected during a campaign.
"""

from __future__ import annotations

from abc import ABC
from collections import defaultdict
from fnmatch import fnmatch
from os import path, walk
from typing import Dict, Iterable, List, Optional, Union, Any

from yaml import safe_load as load_yaml

from metrics.scalpel.config.format import CampaignFormat, InputSetFormat
from metrics.scalpel.config.inputset import create_input_set_reader
from metrics.scalpel.listener import CampaignParserListener
from metrics.scalpel.config.pattern import UserDefinedPattern, compile_named_pattern, compile_regex, \
    AbstractUserDefinedPattern, UserDefinedPatterns, NullUserDefinedPattern


class LogData:
    """
    The LogData contains all the information allowing to retrieve a value from
    an experiment-ware output file.
    """

    def __init__(self, name: str, pattern: UserDefinedPattern) -> None:
        """
        Creates a new LogData.

        :param name: The name of the log data.
        :param pattern: The pattern identifying the log data.
        """
        self._name = name
        self._pattern = pattern

    def get_name(self) -> str:
        """
        Gives the name of this log data.

        :return: The name of this log data.
        """
        return self._name

    def extract_value_from(self, string: str) -> Optional[str]:
        """
        Extracts the value corresponding to this log data from the given string.

        :param string: The string to extract data from.

        :return: The value extracted from the string, or None if this log data
                 does not appear in the string.
        """
        return self._pattern.search(string)


class ScalpelConfiguration:
    """
    The ScalpelConfiguration describes both the context of the campaign and the
    relevant values to retrieve from this campaign.
    """

    def __init__(self, fmt: Optional[CampaignFormat], has_header: bool, quote: str, separator: str, main_file: str,
                 data_files: Optional[List[str]],
                 log_datas: Optional[Dict[str, List[LogData]]],
                 hierarchy_depth: Optional[int],
                 experiment_ware_depth: Optional[int],
                 custom_parser: Optional[str], file_name_meta: FileNameMetaConfiguration) -> None:
        """
        Creates a new ScalpelConfiguration.

        :param fmt: The format in which the results of the campaign are stored.
                    If None, the format will be guessed on a best effort basis.
        :param has_header:
        :param quote:
        :param separator:
        :param main_file: The path of the main file containing data about the
                          campaign.
        :param data_files: The names of the files to be considered for each experiment
                           (wildcards are allowed).
        :param log_datas: The description of the data to extract from the different
                          files of the campaign.
        :param custom_parser: The (completely specified) class of the parser to use to
                              parse the campaign.
        """
        assert file_name_meta is not None
        self._format = fmt
        self._has_header = has_header
        self._quote = quote
        self._sep = separator
        self._main_file = main_file
        self._data_files = data_files
        self._log_datas = log_datas
        self._custom_parser = custom_parser
        self._hierarchy_depth = hierarchy_depth
        self._experiment_ware_depth = experiment_ware_depth
        self._file_name_meta = file_name_meta

    def get_main_file(self) -> str:
        """
        Gives the main file of the campaign, which contains all the data
        about the campaign.

        :return: The path of the main file of the campaign.
        """
        return self._main_file

    def get_format(self) -> CampaignFormat:
        """
        Gives the format of the campaign to parse.

        :return: The format of the campaign.

        :raises: A ValueError is raised if the format was not specified and
                 guessing the format of the campaign has failed.
        """
        return self._format

    def has_header(self) -> bool:
        return self._has_header

    def get_quote_char(self) -> str:
        return self._quote

    def get_separator(self) -> str:
        return self._sep

    def is_to_be_parsed(self, file: str) -> bool:
        """
        CHecks whether the given file must be parsed by Scalpel.

        :param file: The name of the file to check (not its path).

        :return: Whether the file must be parsed.
        """
        if self._log_datas is not None:
            if file in self._log_datas.keys():
                return True

        if self._data_files is not None:
            if any(fnmatch(file, data_file) for data_file in self._data_files):
                return True

        return False

    def get_files(self) -> Iterable[str]:
        """
        Gives the files that must be parsed to retrieve the data to consider
        about the campaign.

        :return: The names of the files to parse.
        """
        if self._log_datas is None:
            return [self._main_file]
        return self._log_datas.keys()

    def get_data_in(self, filename: str) -> List[LogData]:
        """
        Gives the data to retrieve from the given file.

        :param filename: The name of the file from which to extract data.

        :return: The description of the data to extract from the file.
        """
        if None in self._log_datas:
            return self._log_datas[None]
        return self._log_datas[filename]

    def get_hierarchy_depth(self):
        depth = self._hierarchy_depth
        if depth is None:
            return 1
        return int(depth)

    def get_experiment_ware_depth(self):
        depth = self._experiment_ware_depth
        if depth is None:
            return None
        return int(depth)

    def get_custom_parser(self) -> Optional[str]:
        """
        Gives the (completely specified) class of a custom parser to use.

        :return: The class of the custom parser to use, if any.
        """
        return self._custom_parser

    def get_file_name_meta(self) -> FileNameMetaConfiguration:
        return self._file_name_meta


class ConfigurationIterator:
    """
    The ConfigurationIterator allows to iterate over a specific part of
    Scalpel's configuration.
    """

    def has_next(self) -> bool:
        """
        Checks whether there is a next configuration element.

        :return: If there is a next configuration element.
        """
        raise NotImplementedError('Method "has_next()" is abstract!')

    def next(self) -> None:
        """
        Moves to the next configuration element.
        By default, this method does nothing.
        """
        pass


class EmptyConfigurationIterator(ConfigurationIterator):
    """
    The EmptyConfigurationIterator is the parent class for all ConfigurationIterator
    that do not contain any element.
    """

    def has_next(self) -> bool:
        """
        Checks whether there is a next configuration element.

        :return: If there is a next configuration element.
        """
        return False


class ListConfigurationIterator(ConfigurationIterator):
    """
    The ListConfigurationIterator adapts a classical iterable to a
    ConfigurationIterator.
    """

    def __init__(self, adaptee: Iterable):
        """
        Creates a new ListConfigurationIterator.

        :param adaptee: The iterable element to adapt.
        """
        self._adaptee = list(adaptee)
        self._index = 0

    def has_next(self) -> bool:
        """
        Checks whether there is a next configuration element.

        :return: If there is a next configuration element.
        """
        return self._index < len(self._adaptee)

    def current(self) -> Any:
        """
        Checks whether there is a next configuration element.

        :return: The current configuration element.
        """
        return self._adaptee[self._index]

    def next(self):
        """
        Moves to the next configuration element.

        By default, this method does nothing.
        """
        self._index += 1


class MappingConfiguration(ConfigurationIterator, ABC):
    """
    The MappingConfiguration defines the property of the mapping configuration.
    """

    def get_scalpel_key(self) -> str:
        """
        Gives the key expected by Scalpel for the current element.

        :return: The key expected by Scalpel.
        """
        raise NotImplementedError('Method "get_scalpel_key()" is abstract!')

    def get_campaign_key(self) -> Union[str, List[str]]:
        """
        Gives the actual key(s) appearing in the campaign for the current element.

        :return: The actual key of the campaign.
        """
        raise NotImplementedError('Method "get_campaign_key()" is abstract!')


class EmptyMappingConfiguration(EmptyConfigurationIterator, MappingConfiguration):
    """
    The EmptyMappingConfiguration is a MappingConfiguration with no element.
    """

    def get_scalpel_key(self) -> str:
        """
        Gives the key expected by Scalpel for the current element.

        :return: The key expected by Scalpel.
        """
        raise ValueError('Empty mapping configuration!')

    def get_campaign_key(self) -> Union[str, List[str]]:
        """
        Gives the actual key(s) appearing in the campaign for the current element.

        :return: The actual key of the campaign.
        """
        raise ValueError('Empty mapping configuration!')


class DictionaryMappingConfiguration(ListConfigurationIterator, MappingConfiguration):
    """
    The DictionaryMappingConfiguration allows to extract a MappingConfiguration from a dictionary.
    """

    def __init__(self, mapping: Dict[str, Union[str, List[str]]]):
        """
        Creates a new DictionaryMappingConfiguration.

        :param mapping: The dictionary containing the configuration.
        """
        super().__init__(mapping.keys())
        self._mapping = mapping

    def get_scalpel_key(self) -> str:
        """
        Gives the key expected by Scalpel for the current element.

        :return: The key expected by Scalpel.
        """
        return self.current()

    def get_campaign_key(self) -> Union[str, List[str]]:
        """
        Gives the actual key(s) appearing in the campaign for the current element.

        :return: The actual key of the campaign.
        """
        return self._mapping[self.current()]


class RawDataConfiguration(ConfigurationIterator, ABC):
    """
    The MappingConfiguration defines the property of the raw data configuration.
    """

    def get_name(self) -> str:
        """
        Gives the name of the current raw data.

        :return: The name of the raw data.
        """
        raise NotImplementedError('Method "get_campaign_key()" is abstract!')

    def get_file(self) -> str:
        """
        Gives the file from which to retrieve the current raw data.

        :return: The file containing the raw data.
        """
        raise NotImplementedError('Method "get_file()" is abstract!')

    def get_simplified_pattern(self) -> Optional[str]:
        """
        Gives the simplified pattern identifying the current raw data.

        :return: The simplified pattern for the raw data, if any.
        """
        raise NotImplementedError('Method "get_simplified_pattern()" is abstract!')

    def get_regex_pattern(self) -> Optional[str]:
        """
        Gives the regular expression identifying the current raw data.

        :return: The regular expression for the raw data, if any.
        """
        raise NotImplementedError('Method "get_regex_pattern()" is abstract!')

    def get_regex_group(self) -> Optional[int]:
        """
        Gives the group identifying the current raw data in the regular expression.

        :return: The group in the regular expression, if any.
        """
        raise NotImplementedError('Method "get_regex_group()" is abstract!')

    def get_compiled_pattern(self) -> UserDefinedPattern:
        """
        Gives the compiled pattern identifying the current raw data.

        :return: The compiled pattern.

        :raises ValueError: A ValueError is raised if no simplified pattern nor
                            regular expression was specified for the raw data.
        """
        # First, we look for a named pattern.
        simplified_pattern = self.get_simplified_pattern()
        if simplified_pattern is not None:
            return compile_named_pattern(simplified_pattern)

        # There is no look pattern: trying a regular expression.
        regex = self.get_regex_pattern()
        group = self.get_regex_group()
        if regex is not None:
            group = 1 if group is None else group
            return compile_regex(regex, group)

        # The description of the data is missing!
        raise ValueError('A pattern or regex is missing!')


class EmptyRawDataConfiguration(EmptyConfigurationIterator, RawDataConfiguration):
    """
    The EmptyRawDataConfiguration is a RawDataConfiguration with no element.
    """

    def get_name(self) -> str:
        """
        Gives the name of the current raw data.

        :return: The name of the raw data.
        """
        raise ValueError('Empty raw data configuration!')

    def get_file(self) -> str:
        """
        Gives the file from which to retrieve the current raw data.

        :return: The file containing the raw data.
        """
        raise ValueError('Empty raw data configuration!')

    def get_simplified_pattern(self) -> Optional[str]:
        """
        Gives the simplified pattern identifying the current raw data.

        :return: The simplified pattern for the raw data, if any.
        """
        raise ValueError('Empty raw data configuration!')

    def get_regex_pattern(self) -> Optional[str]:
        """
        Gives the regular expression identifying the current raw data.

        :return: The regular expression for the raw data, if any.
        """
        raise ValueError('Empty raw data configuration!')

    def get_regex_group(self) -> Optional[int]:
        """
        Gives the group identifying the current raw data in the regular expression.

        :return: The group in the regular expression, if any.
        """
        raise ValueError('Empty raw data configuration!')


class DictionaryRawDataConfiguration(ListConfigurationIterator, RawDataConfiguration):
    """
    The DictionaryRawDataConfiguration allows to extract a RawDataConfiguration from a
    list of dictionaries.
    """

    def get_name(self) -> str:
        """
        Gives the name of the current raw data.

        :return: The name of the raw data.
        """
        return self.current().get('log-data')

    def get_file(self) -> str:
        """
        Gives the file from which to retrieve the current raw data.

        :return: The file containing the raw data.
        """
        return self.current().get('file')

    def get_simplified_pattern(self) -> Optional[str]:
        """
        Gives the simplified pattern identifying the current raw data.

        :return: The simplified pattern for the raw data, if any.
        """
        return self.current().get('pattern')

    def get_regex_pattern(self) -> Optional[str]:
        """
        Gives the regular expression identifying the current raw data.

        :return: The regular expression for the raw data, if any.
        """
        return self.current().get('regex')

    def get_regex_group(self) -> Optional[int]:
        """
        Gives the group identifying the current raw data in the regular expression.

        :return: The group in the regular expression, if any.
        """
        return self.current().get('group')


class DictionaryConfiguration:
    def __init__(self, dic):
        self._dict = dic

    def get(self, key: str):
        return self._dict.get(key)


class FileNameMetaConfiguration:
    """
    The MappingConfiguration defines the property of the raw data configuration.
    """

    def get_simplified_pattern(self) -> Optional[str]:
        """
        Gives the simplified pattern identifying the current filename.

        :return: The simplified pattern for the raw data, if any.
        """
        raise NotImplementedError('Method "get_simplified_pattern()" is abstract!')

    def get_regex_pattern(self) -> Optional[str]:
        """
        Gives the regular expression identifying the current filename.

        :return: The regular expression for the raw data, if any.
        """
        raise NotImplementedError('Method "get_regex_pattern()" is abstract!')

    def get_input_group(self) -> Optional[int]:
        """
        Gives the group identifying the input name in the regular expression.

        :return: The group in the regular expression, if any.
        """
        raise NotImplementedError('Method "get_regex_group()" is abstract!')

    def get_experiment_ware_group(self) -> Optional[int]:
        """
        Gives the group identifying the experiment ware in the regular expression.

        :return: The group in the regular expression, if any.
        """
        raise NotImplementedError('Method "get_regex_group()" is abstract!')

    def get_compiled_pattern(self) -> AbstractUserDefinedPattern:
        """
        Gives the compiled pattern identifying the current raw data.

        :return: The compiled pattern.

        :raises ValueError: A ValueError is raised if no simplified pattern nor
                            regular expression was specified for the raw data.
        """
        # First, we look for a named pattern.
        simplified_pattern = self.get_simplified_pattern()
        if simplified_pattern is not None:
            return compile_named_pattern(simplified_pattern)

        # There is no look pattern: trying a regular expression.
        regex = self.get_regex_pattern()
        experiment_ware_group = self.get_experiment_ware_group()
        input_group = self.get_input_group()
        if regex is not None:
            user_defined_patterns = UserDefinedPatterns()
            if experiment_ware_group is not None:
                user_defined_patterns.add(compile_regex(regex, experiment_ware_group))
            if input_group is not None:
                user_defined_patterns.add(compile_regex(regex, input_group))
            return user_defined_patterns

        # The description of the data is missing!
        raise ValueError('A pattern or regex is missing!')


class EmptyFileNameMetaConfiguration(FileNameMetaConfiguration):
    """
    The EmptyFileNameMetaConfiguration is a RawDataConfiguration with no element.
    """

    def get_simplified_pattern(self) -> Optional[str]:
        """
        Gives the simplified pattern identifying the current raw data.

        :return: The simplified pattern for the raw data, if any.
        """
        raise ValueError('Empty raw data configuration!')

    def get_regex_pattern(self) -> Optional[str]:
        """
        Gives the regular expression identifying the current raw data.

        :return: The regular expression for the raw data, if any.
        """
        raise ValueError('Empty raw data configuration!')

    def get_input_group(self) -> Optional[int]:
        raise ValueError('Empty raw data configuration!')

    def get_experiment_ware_group(self) -> Optional[int]:
        raise ValueError('Empty raw data configuration!')

    def get_compiled_pattern(self) -> AbstractUserDefinedPattern:
        return NullUserDefinedPattern()


class DictionaryFileNameMetaConfiguration(FileNameMetaConfiguration, DictionaryConfiguration):

    def get_simplified_pattern(self) -> Optional[str]:
        return self.get('pattern')

    def get_regex_pattern(self) -> Optional[str]:
        return self.get('regex')

    def get_input_group(self) -> Optional[int]:
        return self.get('input_group')

    def get_experiment_ware_group(self) -> Optional[int]:
        return self.get('experiment_ware')


class ScalpelConfigurationBuilder:
    """
    The ScalpelConfigurationBuilder allows to build Scalpel's configuration.
    """

    def __init__(self, listener: CampaignParserListener) -> None:
        """
        Creates a new ScalpelConfigurationBuilder.

        :param listener: The listener to set up and notify while parsing the
                         configuration file.
        """
        self._listener = listener
        self._main_file = None
        self._format = None
        self._hierarchy_depth = None
        self._experiment_ware_depth = None
        self._data_files = None
        self._log_datas = defaultdict(list)
        self._custom_parser = None
        self._header = True
        self._sep = ','
        self._quote = None
        self._file_name_meta = EmptyFileNameMetaConfiguration()

    def build(self) -> ScalpelConfiguration:
        """
        Builds the configuration of Scalpel, as specified by the user.

        :return: The built configuration.
        """
        self._listener.start_campaign()
        self.read_mapping()
        self.read_metadata()
        self.read_setup()
        self.read_experiment_wares()
        self.read_input_set()
        self.read_source()
        self.read_data()
        return ScalpelConfiguration(self._format, self._header, self._quote, self._sep, self._main_file,
                                    self._data_files, self._log_datas,
                                    self._hierarchy_depth,
                                    self._experiment_ware_depth,
                                    self._custom_parser, self._file_name_meta)

    def read_mapping(self) -> None:
        """
        Reads the mapping allowing to retrieve the data wanted by Scalpel from
        the experiment files.
        """
        mapping = self._get_mapping()
        while mapping.has_next():
            scalpel_key = mapping.get_scalpel_key()
            campaign_key = mapping.get_campaign_key()
            self._listener.add_key_mapping(scalpel_key, campaign_key)
            mapping.next()

    def _get_mapping(self) -> MappingConfiguration:
        """
        Gives the mapping configuration object allowing to retrieve the data
        expected by Scalpel from the experiment files.

        :return: The configuration for the mapping.
        """
        raise NotImplementedError('Method "_get_mapping()" is abstract!')

    def read_metadata(self) -> None:
        """
        Reads the description of the campaign to parse.
        """
        self._log_data('name', self._get_campaign_name())
        self._log_data('date', self._get_campaign_date())

    def _get_campaign_name(self) -> Optional[str]:
        """
        Gives the name of the campaign being considered.

        :return: The name of the campaign.
        """
        raise NotImplementedError('Method "_get_campaign_name()" is abstract!')

    def _get_campaign_date(self) -> Optional[str]:
        """
        Gives the date of the campaign being considered.

        :return: The date of the campaign.
        """
        raise NotImplementedError('Method "_get_campaign_date()" is abstract!')

    def read_setup(self) -> None:
        """
        Reads the description of the experimental setup.
        """
        self._log_data('os', self._get_os_description())
        self._log_data('cpu', self._get_cpu_description())
        self._log_data('memory', self._get_total_memory())
        self._log_data('timeout', self._get_time_out())
        self._log_data('memout', self._get_memory_out())

    def _get_os_description(self) -> Optional[str]:
        """
        Gives the description of the operating system on which the campaign has
        been executed.

        :return: The description of the OS.
        """
        raise NotImplementedError('Method "_get_os_description()" is abstract!')

    def _get_cpu_description(self) -> Optional[str]:
        """
        Gives the description of the CPU of the machine(s) on which the campaign
        has been executed.

        :return: The description of the CPU.
        """
        raise NotImplementedError('Method "_get_cpu_description()" is abstract!')

    def _get_total_memory(self) -> Optional[str]:
        """
        Gives the total amount of memory available on the machine(s) on which the
        campaign has been executed.

        :return: The total amount of memory.
        """
        raise NotImplementedError('Method "_get_total_memory()" is abstract!')

    def _get_time_out(self) -> Optional[str]:
        """
        Gives the time limit set to the experiments in this campaign.

        :return: The configured time limit.
        """
        raise NotImplementedError('Method "_get_time_out()" is abstract!')

    def _get_memory_out(self) -> Optional[str]:
        """
        Gives the memory limit set to the experiments in this campaign.

        :return: The set configured limit.
        """
        raise NotImplementedError('Method "_get_memory_out()" is abstract!')

    def read_experiment_wares(self) -> None:
        """
        Reads the experiment-wares that are considered in the campaign being
        parsed by Scalpel.
        """
        raise NotImplementedError('Method "read_experiment_wares()" is abstract!')

    def read_input_set(self) -> None:
        """
        Reads the input set considered in the campaign being parsed by Scalpel.
        """
        raise NotImplementedError('Method "read_input_data()" is abstract!')

    def read_source(self) -> None:
        """
        Reads the description of the source from which the campaign is to
        be parsed.
        """
        self._main_file = self._get_campaign_path()
        self._format = self._guess_format()
        self._format = self._get_format()
        self._header = self._has_header()
        self._quote = self._quote_char()
        self._sep = self._separator()
        self._hierarchy_depth = self._get_hierarchy_depth()
        self._experiment_ware_depth = self._get_experiment_ware_depth()
        self._custom_parser = self._get_custom_parser()

    def _get_campaign_path(self) -> Iterable[str]:
        """
        Gives the path of the file containing all the data about the campaign.
        This file may be either a regular file or a directory.

        :return: The path to the main file of the campaign.
        """
        raise NotImplementedError('Method "_get_campaign_path()" is abstract!')

    def _get_format(self) -> Optional[CampaignFormat]:
        """
        Gives the format of the campaign to parse.
        If not specified, the format is guessed on a best effort basis.

        :return: The format of the campaign to parse, if any.
        """
        raise NotImplementedError('Method "_get_format()" is abstract!')

    def _guess_format(self) -> Optional[CampaignFormat]:
        """
        Guesses the format of the campaign to parse.

        :return: The guessed format of the campaign, or None if it could
                 not be guessed.
        """
        if path.isdir(self._main_file[0]):
            return self._guess_directory_format()
        if path.exists(self._main_file[0]):
            return self._guess_regular_format()
        return None

    def _guess_directory_format(self) -> Optional[CampaignFormat]:
        """
        Guesses the format of the campaign to parse when stored in a directory.

        :return: The format of the campaign, guessed from the deepness of the
                 file hierarchy rooted at the main file of this campaign.
        """
        for _, dirs, _ in walk(self._main_file[0]):
            if dirs:
                return CampaignFormat.DEEP_LOG_DIRECTORY
        return CampaignFormat.FLAT_LOG_DIRECTORY

    def _guess_regular_format(self) -> Optional[CampaignFormat]:
        """
        Guesses the format of the campaign to parse when stored in a regular file.

        :return: The format of the campaign, guessed from the extension of its
                 main file, or None if it could not be guessed.
        """
        try:
            index = self._main_file[0].rindex('.')
            return CampaignFormat.value_of(self._main_file[0][index + 1:])
        except ValueError:
            return None

    def _has_header(self) -> bool:
        """
        Checks whether the input file to parse has a header.

        :return: If the input file to parse has a header.
        """
        raise NotImplementedError('Method "_has_header()" is abstract!')

    def _quote_char(self) -> str:
        """
        :return: Return the quote char
        """
        raise NotImplementedError('Method "_quote_char()" is abstract!')

    def _separator(self) -> str:
        """
        :return: Return the separator
        """
        raise NotImplementedError('Method "_separator()" is abstract!')

    def _get_hierarchy_depth(self) -> Optional[int]:
        """
        Gives the depth of the hierarchy to explore, when the campaign is
        in the deep log hierarchy format.

        :return: The depth of the hierarchy, if specified.
        """
        raise NotImplementedError('Method "_get_hierarchy_depth()" is abstract!')

    def _get_experiment_ware_depth(self) -> Optional[int]:
        """
        Gives the depth of the directory corresponding to the experiment-ware
        being executed, when the campaign is in the deep log hierarchy format.

        :return: The depth of the experiment-ware directory, if any.
        """
        raise NotImplementedError('Method "_get_experiment_ware_depth()" is abstract!')

    def _get_custom_parser(self) -> Optional[str]:
        """
        Gives the (completely specified) class of the custom parser to use to parse
        the campaign, if any.

        :return: The class of the parser to use
        """
        raise NotImplementedError('Method "_get_custom_parser()" is abstract!')

    def read_data(self) -> None:
        """
        Reads the files from which Scalpel will extract relevant data for the
        analysis.
        Such files are only meaningful when the campaign is stored in a
        directory.
        """
        raw_data = self._get_raw_data()
        self._file_name_meta = self._get_file_name_meta()
        while raw_data.has_next():
            file = raw_data.get_file()
            name = raw_data.get_name()
            pattern = raw_data.get_compiled_pattern()
            self._log_datas[file].append(LogData(name, pattern))
            raw_data.next()
        self._data_files = self._get_data_files()

    def _get_file_name_meta(self) -> FileNameMetaConfiguration:
        raise NotImplementedError('Method "_get_file_name_meta()" is abstract!')

    def _get_raw_data(self) -> RawDataConfiguration:
        """
        Gives the raw data configuration, which describes how to extract data
        from the log files of the experiment-wares.
        Such data is only meaningful when the campaign is stored in a
        directory.

        :return: The raw data configuration.
        """
        raise NotImplementedError('Method "_get_raw_data()" is abstract!')

    def _get_data_files(self) -> Iterable[str]:
        """
        Gives the output files to consider for each experiment, which must be in
        a format that Scalpel natively recognizes (JSON, CSV, etc.).
        Such files are only meaningful when the campaign is stored in a "deep"
        file hierarchy.

        :return: The raw data configuration.
        """
        raise NotImplementedError('Method "_get_data_files()" is abstract!')

    def _log_data(self, key: str, value: Optional[str]) -> None:
        """
        Notifies the listener about data that has been read.

        :param key: The key identifying the read data.
        :param value: The value that has been read.
        """
        if value is not None:
            self._listener.log_data(key, value)


class DictionaryScalpelConfigurationBuilder(ScalpelConfigurationBuilder):
    """
    The DictionaryScalpelConfigurationBuilder builds Scalpel's configuration
    from a dictionary describing this configuration.
    Such a configuration is most likely obtained from a YAML file.
    """

    def __init__(self, dict_config: dict, listener) -> None:
        super().__init__(listener)
        self._dict_config = dict_config

    def _get_mapping(self) -> MappingConfiguration:
        """
        Gives the mapping configuration object allowing to retrieve the data
        expected by Scalpel from the experiment files.

        :return: The configuration for the mapping.
        """
        mapping = self._get('data').get('mapping')
        return EmptyMappingConfiguration() if mapping is None else DictionaryMappingConfiguration(mapping)

    def _get_campaign_name(self) -> str:
        """
        Gives the name of the campaign being considered.

        :return: The name of the campaign.
        """
        return self._dict_config.get('name')

    def _get_campaign_date(self) -> str:
        """
        Gives the date of the campaign being considered.

        :return: The date of the campaign.
        """
        return self._dict_config.get('date')

    def _get_os_description(self) -> str:
        """
        Gives the description of the operating system on which the campaign has been executed.

        :return: The description of the OS.
        """
        return self._get('setup').get('os')

    def _get_cpu_description(self) -> str:
        """
        Gives the description of the CPU of the machine(s) on which the campaign
        has been executed.

        :return: The description of the CPU.
        """
        return self._get('setup').get('cpu')

    def _get_total_memory(self) -> str:
        """
        Gives the total amount of memory available on the machine(s) on which the
        campaign has been executed.

        :return: The total amount of memory.
        """
        return self._get('setup').get('ram')

    def _get_time_out(self) -> str:
        """
        Gives the time limit set to the experiments in this campaign.

        :return: The set time limit.
        """
        return str(self._get('setup').get('timeout'))

    def _get_memory_out(self) -> str:
        """
        Gives the memory limit set to the experiments in this campaign.

        :return: The set memory limit.
        """
        return str(self._get('setup').get('memout'))

    def read_experiment_wares(self) -> None:
        """
        Reads the experiment-wares that are considered in the campaign being
        parsed by Scalpel.
        """

        experiment_wares = self._dict_config.get('experiment-wares')
        if experiment_wares is not None:
            for xp_ware in experiment_wares:
                self._listener.start_experiment_ware()
                self._listener.log_data('name', xp_ware)
                self._listener.end_experiment_ware()


    def read_input_set(self) -> None:
        """
        Reads the input set considered in the campaign being parsed by Scalpel.
        """

        input_set = self._dict_config.get('input-set')
        if input_set is None:
            return
        self._listener.start_input_set()
        fmt = InputSetFormat.value_of(input_set['type'])
        name = input_set['name']
        self._listener.log_data('name', name)
        paths = DictionaryScalpelConfigurationBuilder._as_list(input_set['path-list'])
        kwargs = {}

        if 'family' in self._get('input-set'):
            kwargs['family'] = self._get('input-set').get('family')

        if 'input-name' in self._get('input-set'):
            kwargs['name'] = self._get('input-set').get('input-name')

        extensions = self._get('input-set').get('extensions')
        if extensions is not None:
            kwargs['extensions'] = extensions

        create_input_set_reader(fmt, **kwargs)(self._listener, paths)
        self._listener.end_input_set()

    def _get_campaign_path(self) -> Iterable[str]:
        """
        Gives the path of the file containing all the data about the campaign.
        This file may be either a regular file or a directory.

        :return: The path to the main file of the campaign.
        """
        campaign_path = self._get('source').get('path')
        if campaign_path is None:
            raise ValueError
        if isinstance(campaign_path, list):
            return campaign_path
        return [campaign_path]

    def _get_format(self) -> Optional[CampaignFormat]:
        """
        Gives the format of the campaign to parse.
        If not specified, the format is guessed on a best effort basis.

        :return: The format of the campaign to parse, if any.
        """
        fmt = self._get('source').get('format')
        if fmt is None:
            return self._format
        return CampaignFormat.value_of(fmt)

    def _has_header(self) -> bool:
        """
        Checks whether the input file to parse has a header.

        :return: If the input file to parse has a header.
        """
        has_header = self._get('source').get('has-header')
        return has_header is None or has_header

    def _quote_char(self) -> str:
        """
        :return: Return the quote char
        """
        return self._get('source').get('quote-char')

    def _separator(self) -> str:
        """
        :return: Return the separator
        """
        sep = self._get('source').get('separator')
        return sep if sep is not None else ','

    def _get_hierarchy_depth(self) -> Optional[int]:
        """
        Gives the depth of the hierarchy to explore, when the campaign is
        in the deep log hierarchy format.

        :return: The depth of the hierarchy, if specified.
        """
        return self._get('source').get('hierarchy-depth')

    def _get_experiment_ware_depth(self) -> Optional[int]:
        """
        Gives the depth of the directory corresponding to the experiment-ware
        being executed, when the campaign is in the deep log hierarchy format.

        :return: The depth of the experiment-ware directory, if any.
        """
        return self._get('source').get('experiment-ware')

    def _get_custom_parser(self) -> Optional[str]:
        """
        Gives the (completely specified) class of the custom parser to use to parse
        the campaign, if any.

        :return: The class of the parser to use
        """
        return self._get('source').get('parser')

    def _get_file_name_meta(self) -> FileNameMetaConfiguration:
        file_name_meta = self._get('data').get('file-name-meta')
        if file_name_meta is None:
            return EmptyFileNameMetaConfiguration()
        return DictionaryFileNameMetaConfiguration(file_name_meta)

    def _get_raw_data(self) -> RawDataConfiguration:
        """
        Gives the raw data configuration, which describes how to extract data
        from the log files of the experiment-wares.
        Such data is only meaningful when the campaign is stored in a
        directory.

        :return: The raw data configuration.
        """
        data = self._get('data').get('raw-data')
        data_list = DictionaryScalpelConfigurationBuilder._as_list(data)
        return DictionaryRawDataConfiguration(data_list)

    def _get_data_files(self) -> Iterable[str]:
        """
        Gives the output files to consider for each experiment, which must be in
        a format that Scalpel natively recognizes (JSON, CSV, etc.).
        Such files are only meaningful when the campaign is stored in a "deep"
        file hierarchy.

        :return: The raw data configuration.
        """
        files = self._get('data').get('data-files')
        return DictionaryScalpelConfigurationBuilder._as_list(files)

    def _get(self, key: str) -> dict:
        """
        Gives the dictionary containing the configuration for the specified key.

        :return: The configuration for the specified key, or an empty dictionary
                 if the configuration is not specified.
        """
        config = self._dict_config.get(key)
        return {} if config is None else config

    @staticmethod
    def _as_list(obj: Any) -> list:
        if obj is None:
            return []

        elif isinstance(obj, list):
            return obj

        else:
            return [obj]


def read_configuration(yaml_file: str, listener: CampaignParserListener) -> ScalpelConfiguration:
    """
    Loads Scalpel's configuration from the given YAML file.

    :param yaml_file: The path of the file to load the configuration from.
    :param listener: The listener to notify about the context of the campaign
                     while reading the configuration.

    :return: The read configuration.
    """
    with open(yaml_file, 'r') as yaml_stream:
        yaml = load_yaml(yaml_stream)
        builder = DictionaryScalpelConfigurationBuilder(yaml, listener)
        return builder.build()
