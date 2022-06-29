###############################################################################
#                                                                             #
#  Scalpel - A Metrics Module                                                 #
#  Copyright (c) 2019-2022 - Univ Artois & CNRS, Exakis Nelite                #
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
This module provides classes for saving the configuration of Scalpel.
"""
from collections import defaultdict
import yaml
from metrics.scalpel.config.wrapper import *


class FileNameMetaConfigurationWrapperSaverDecorator(IFileNameMetaConfigurationWrapper):

    def __init__(self, decorated, dict_config):
        self._decorated = decorated
        self._dict_config = {}

    def get_simplified_pattern(self) -> Optional[str]:
        pattern = self._decorated.get_simplified_pattern()
        self._dict_config['pattern'] = pattern
        return pattern

    def get_regex_pattern(self) -> Optional[str]:
        pattern = self._decorated.get_regex_pattern()
        self._dict_config['regex'] = pattern
        return pattern

    def get_groups(self) -> Iterable[Tuple[str, int]]:
        groups = self._decorated.get_groups()
        self._dict_config['groups'] = {k: v for k, v in groups}
        return groups

    def is_exact(self) -> bool:
        exact = self._decorated.is_exact()
        self._dict_config['is-exact'] = exact
        return exact


class InputSetWrapperSaverDecorator(IInputSetWrapper):

    def __init__(self, decorated, dict_config):
        self._decorated = decorated
        self._dict_config = dict_config

    def get_name(self) -> str:
        name = self._decorated.get_name()
        self._dict_config['input-set']['name'] = name
        return name

    def get_type(self) -> str:
        type = self._decorated.get_type()
        self._dict_config['input-set']['type'] = type
        return type

    def get_extensions(self) -> List[str]:
        extensions = self._decorated.get_extensions()
        self._dict_config['input-set']['extensions'] = extensions
        return extensions

    def get_file_name_meta(self) -> IFileNameMetaConfigurationWrapper:
        self._dict_config['input-set']['file-name-meta'] = {}
        return FileNameMetaConfigurationWrapperSaverDecorator(self._decorated.get_file_name_meta(),
                                                              self._dict_config['input-set'][
                                                                  'file-name-meta'])

    def get_files(self) -> List[Any]:
        files = self._decorated.get_files()
        self._dict_config['input-set']['files'] = files
        return files


class RawDataConfigurationWrapperSaverDecorator(IRawDataConfigurationWrapper):

    def __init__(self, decorated, list_config):
        self._decorated = decorated
        self._dict_config = {}
        list_config.append(self._dict_config)

    def get_file(self) -> str:
        file = self._decorated.get_file()
        self._dict_config['file'] = file
        return file

    def get_simplified_pattern(self) -> Optional[str]:
        pattern = self._decorated.get_simplified_pattern()
        self._dict_config['pattern'] = pattern
        return pattern

    def get_regex_pattern(self) -> Optional[str]:
        pattern = self._decorated.get_regex_pattern()
        self._dict_config['regex'] = pattern
        return pattern

    def get_groups(self) -> Iterable[Tuple[str, int]]:
        groups = self._decorated.get_groups()
        self._dict_config['groups'] = {k: v for k, v in groups}
        return groups

    def is_exact(self) -> bool:
        exact = self._decorated.is_exact()
        self._dict_config['is-exact'] = exact
        return exact


class DataFileConfigurationWrapperSaverDecorator(IDataFileConfigurationWrapper):

    def __init__(self, decorated, list_config):
        self._decorated = decorated
        self._dict_config = {}
        list_config.append(self._dict_config)

    def get_name(self) -> str:
        name = self._decorated.get_name()
        self._dict_config['name'] = name
        return name

    def has_name_as_prefix(self) -> bool:
        name_as_prefix = self._decorated.has_name_as_prefix()
        self._dict_config['name-as-prefix'] = name_as_prefix
        return name_as_prefix

    def get_format(self) -> Optional[str]:
        fmt = self._decorated.get_format()
        self._dict_config['format'] = fmt
        return fmt

    def has_header(self) -> bool:
        header = self._decorated.has_header()
        self._dict_config['has-header'] = header
        return header

    def get_quote_char(self) -> Optional[str]:
        quote_char = self._decorated.get_quote_char()
        self._dict_config['quote-char'] = quote_char
        return quote_char

    def get_separator(self) -> Optional[str]:
        separator = self._decorated.get_separator()
        self._dict_config['separator'] = separator
        return separator

    def get_custom_parser(self) -> Optional[str]:
        parser = self._decorated.get_custom_parser()
        self._dict_config['parser'] = parser
        return parser


class ScalpelConfigurationWrapperSaverDecorator(IScalpelConfigurationWrapper):

    def __init__(self, decorated: IScalpelConfigurationWrapper, file: str):
        self._decorated = decorated
        self._file = file
        self._dict_config = defaultdict(dict)

    def get_campaign_name(self) -> Optional[str]:
        name = self._decorated.get_campaign_name()
        self._dict_config['name'] = name
        return name

    def get_campaign_date(self) -> Optional[str]:
        date = self._decorated.get_campaign_date()
        self._dict_config['date'] = date
        return date

    def get_os_description(self) -> Optional[str]:
        os = self._decorated.get_os_description()
        self._dict_config['setup']['os'] = os
        return os

    def get_cpu_description(self) -> Optional[str]:
        cpu = self._decorated.get_cpu_description()
        self._dict_config['setup']['cpu'] = cpu
        return cpu

    def get_gpu_description(self) -> Optional[str]:
        gpu = self._decorated.get_gpu_description()
        self._dict_config['setup']['gpu'] = gpu
        return gpu

    def get_total_memory(self) -> Optional[str]:
        ram = self._decorated.get_total_memory()
        self._dict_config['setup']['ram'] = ram
        return ram

    def get_time_out(self) -> Optional[str]:
        timeout = self._decorated.get_time_out()
        self._dict_config['setup']['timeout'] = timeout
        return timeout

    def get_memory_out(self) -> Optional[str]:
        memout = self._decorated.get_memory_out()
        self._dict_config['setup']['memout'] = memout
        return memout

    def get_experiment_wares(self) -> List[Dict[str, str]]:
        xp_wares = self._decorated.get_experiment_wares()
        self._dict_config['experiment-wares'] = xp_wares
        return xp_wares

    def get_input_set(self) -> List[IInputSetWrapper]:
        return [InputSetWrapperSaverDecorator(i, self._dict_config) for i in
                self._decorated.get_input_set()]

    def get_campaign_path(self) -> List[str]:
        campaign_path = self._decorated.get_campaign_path()
        self._dict_config['source']['path'] = campaign_path
        return campaign_path

    def get_format(self) -> Optional[str]:
        fmt = self._decorated.get_format()
        self._dict_config['source']['format'] = fmt
        return fmt

    def has_header(self) -> bool:
        header = self._decorated.has_header()
        self._dict_config['source']['has-header'] = header
        return header

    def get_quote_char(self) -> Optional[str]:
        quote_char = self._decorated.get_quote_char()
        self._dict_config['source']['quote-char'] = quote_char
        return quote_char

    def get_separator(self) -> Optional[str]:
        separator = self._decorated.get_separator()
        self._dict_config['source']['separator'] = separator
        return separator

    def get_title_separator(self) -> Optional[str]:
        separator = self._decorated.get_title_separator()
        self._dict_config['source']['title-separator'] = separator
        return separator

    def get_follow_symlinks(self) -> bool:
        follow_symlinks = self._decorated.get_follow_symlinks()
        self._dict_config['source']['follow-symlinks'] = follow_symlinks
        return follow_symlinks

    def get_custom_parser(self) -> Optional[str]:
        parser = self._decorated.get_custom_parser()
        self._dict_config['source']['parser'] = parser
        return parser

    def get_is_success(self) -> List[str]:
        is_success = self._decorated.get_is_success()
        self._dict_config['source']['is-success'] = is_success
        return is_success

    def get_mapping(self) -> Dict[str, List[str]]:
        mapping = self._decorated.get_mapping()
        self._dict_config['data']['mapping'] = mapping
        return mapping

    def get_default_values(self) -> Dict[str, str]:
        default_values = self._decorated.get_default_values()
        self._dict_config['data']['default-values'] = default_values
        return default_values

    def get_ignored_data(self) -> List[str]:
        ignored_data = self._decorated.get_ignored_data()
        self._dict_config['data']['ignored-data'] = ignored_data
        return ignored_data

    def get_file_name_meta(self) -> IFileNameMetaConfigurationWrapper:
        self._dict_config['data']['file-name-meta'] = {}
        return FileNameMetaConfigurationWrapperSaverDecorator(self._decorated.get_file_name_meta(),
                                                              self._dict_config['data'][
                                                                  'file-name-meta'])

    def get_raw_data(self) -> Iterable[IRawDataConfigurationWrapper]:
        self._dict_config['data']['raw-data'] = []
        return [RawDataConfigurationWrapperSaverDecorator(d, self._dict_config['data']['raw-data'])
                for d in self._decorated.get_raw_data()]

    def get_data_files(self) -> Iterable[IDataFileConfigurationWrapper]:
        self._dict_config['data']['data-files'] = []
        return [
            DataFileConfigurationWrapperSaverDecorator(d, self._dict_config['data']['data-files'])
            for d in self._decorated.get_data_files()]

    def get_ignored_files(self) -> List[str]:
        ignored_files = self._decorated.get_ignored_files()
        self._dict_config['data']['ignored-files'] = ignored_files
        return ignored_files

    def save(self):
        with open(self._file, 'w') as outfile:
            yaml.dump({k:v for k, v in self._dict_config.items()}, outfile, default_flow_style=False)
