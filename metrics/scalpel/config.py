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

from os import path, walk
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union

from yaml import safe_load as read_yaml

from metrics.scalpel.format import CampaignFormat, InputSetFormat
from metrics.scalpel.inputset import create_input_set_reader
from metrics.scalpel.listener import CampaignParserListener
from metrics.scalpel.pattern import UserDefinedPattern


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

    def __init__(self, fmt: CampaignFormat, main_file: str,
                 log_datas: Optional[Dict[str, List[LogData]]] = None,
                 custom_parser: Optional[str] = None) -> None:
        """
        Creates a new ScalpelConfiguration.

        :param fmt: The format in which the results of the campaign are stored.
                    If None, the format will be guessed from a best effort basis.
        :param main_file: The path of the main file containing data about the
                          campaign.
        :param log_datas: The description of the data to extract from the different
                          files of the campaign.
        """
        self._format = fmt
        self._main_file = main_file
        self._log_datas = log_datas
        self._custom_parser = custom_parser

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
        if self._format is None:
            return self._guess_format()
        return self._format

    def _guess_format(self) -> CampaignFormat:
        """
        Guesses the format of the campaign to parse.

        :return: The guessed format of the campaign.

        :raises: A ValueError is raised if it is not possible to guess the
                 format of the campaign.
        """
        if path.isdir(self._main_file):
            return self._guess_directory_format()
        if path.exists(self._main_file):
            return self._guess_regular_format()
        raise ValueError(f'{self._main_file}: No such file or directory.')

    def _guess_regular_format(self):
        """
        Guesses the format of the campaign to parse when stored in a regular file.

        :return: The format of the campaign, guessed from the extension of its
                 main file.

        :raises: A ValueError is raised if it is not possible to guess the
                 format of the campaign.
        """
        index = self._main_file.rindex('.')
        return CampaignFormat.value_of(self._main_file[index + 1:])

    def _guess_directory_format(self):
        """
        Guesses the format of the campaign to parse when stored in a directory.

        :return: The format of the campaign, guessed from the deepness of the
                 file hierarchy rooted at the main file of this campaign.
        """
        for _, dirs, _ in walk(self._main_file):
            if dirs:
                return CampaignFormat.DEEP_LOG_DIRECTORY
        return CampaignFormat.FLAT_LOG_DIRECTORY

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
        return self._log_datas[filename]

    def get_custom_parser(self) -> Optional[str]:
        """
        Gives the (completely specified) class of a custom parser to use.

        :return: The class of the custom parser to use, if any.
        """
        return self._custom_parser


class ScalpelConfigurationBuilder:
    """
    The ScalpelConfigurationBuilder allows to build Scalpel's configuration
    from YAML.
    """

    def __init__(self, listener: CampaignParserListener) -> None:
        """
        Creates a new ScalpelConfigurationBuilder.

        :param listener: The listener to set up and notify while parsing the
                         configuration file.
        """
        self._listener = listener
        self._format = None
        self._main_file = None

    def read_mapping(self) -> None:
        """
        Reads the mapping associating each log variable to a variable recognized by Scalpel.
        """
        for scalpel_key, campaign_key in self._get_mapping():
            self._listener.add_key_mapping(scalpel_key, campaign_key)

    def _get_mapping(self) -> Iterable[Tuple[str, Union[List[str], str]]]:
        """
        Gives the mapping associating each log variable to a variable recognized by Scalpel.

        :return: The mapping of the variables
        """
        raise NotImplementedError('Method "_get_mapping()" is abstract!')

    def read_metadata(self) -> None:
        """
        Reads the description of the campaign to parse.
        """
        self._listener.log_data('name', self._get_campaign_name())
        self._listener.log_data('date', self._get_campaign_date())

    def _get_campaign_name(self) -> str:
        """
        Gives the name of the campaign being considered.

        :return: The name of the campaign.
        """
        raise NotImplementedError('Method "_get_campaign_name()" is abstract!')

    def _get_campaign_date(self) -> str:
        """
        Gives the date of the campaign being considered.

        :return: The date of the campaign.
        """
        raise NotImplementedError('Method "_get_campaign_date()" is abstract!')

    def read_setup(self) -> None:
        """
        Reads the description of the experimental setup.
        """
        self._listener.log_data('os', self._get_os_description())
        self._listener.log_data('cpu', self._get_cpu_description())
        self._listener.log_data('memory', self._get_total_memory())
        self._listener.log_data('timeout', self._get_time_out())
        self._listener.log_data('memout', self._get_memory_out())

    def _get_os_description(self) -> str:
        """
        Gives the description of the operating system on which the campaign has been executed.

        :return: The description of the OS.
        """
        raise NotImplementedError('Method "_get_os_description()" is abstract!')

    def _get_cpu_description(self) -> str:
        """
        Gives the description of the CPU of the machine(s) on which the campaign
        has been executed.

        :return: The description of the CPU.
        """
        raise NotImplementedError('Method "_get_cpu_description()" is abstract!')

    def _get_total_memory(self) -> str:
        """
        Gives the total amount of memory available on the machine(s) on which the
        campaign has been executed.

        :return: The total amount of memory.
        """
        raise NotImplementedError('Method "_get_total_memory()" is abstract!')

    def _get_time_out(self) -> str:
        """
        Gives the time limit set to the experiments in this campaign.

        :return: The set time limit.
        """
        raise NotImplementedError('Method "_get_time_out()" is abstract!')

    def _get_memory_out(self) -> str:
        """
        Gives the memory limit set to the experiments in this campaign.

        :return: The set memoru limit.
        """
        raise NotImplementedError('Method "_get_memory_out()" is abstract!')

    def read_experiment_wares(self) -> None:
        raise NotImplementedError('Method "read_experiment_wares()" is abstract!')

    def read_input_set(self) -> None:
        raise NotImplementedError('Method "read_input_data()" is abstract!')

    def read_log_data(self) -> None:
        raise NotImplementedError('Method "read_experiment_data()" is abstract!')

    def read_source(self) -> None:
        raise NotImplementedError('Method "read_source()" is abstract!')

    def build(self) -> ScalpelConfiguration:
        self._listener.start_campaign()
        self.read_mapping()
        self.read_metadata()
        self.read_setup()
        self.read_experiment_wares()
        self.read_input_set()
        self.read_source()
        self.read_log_data()
        return ScalpelConfiguration(self._format, self._main_file)


class DictionaryScalpelConfigurationBuilder(ScalpelConfigurationBuilder):
    """
    The DictionaryScalpelConfigurationBuilder builds Scalpel's configuration
    from a dictionary describing this configuration.
    Such a configuration is most likely obtained from a YAML file.
    """

    def __init__(self, dict_config: dict, listener) -> None:
        super().__init__(listener)
        self._dict_config = dict_config

    def _get_mapping(self):
        """
        Gives the mapping associating each log variable to a variable recognized by Scalpel.

        :return: The mapping of the variables
        """
        return self._dict_config['data']['mapping'].items()

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
        return self._dict_config.get('setup').get('os')

    def _get_cpu_description(self) -> str:
        """
        Gives the description of the CPU of the machine(s) on which the campaign
        has been executed.

        :return: The description of the CPU.
        """
        return self._dict_config.get('setup').get('cpu')

    def _get_total_memory(self) -> str:
        """
        Gives the total amount of memory available on the machine(s) on which the
        campaign has been executed.

        :return: The total amount of memory.
        """
        return self._dict_config.get('setup').get('ram')

    def _get_time_out(self) -> str:
        """
        Gives the time limit set to the experiments in this campaign.

        :return: The set time limit.
        """
        return str(self._dict_config.get('setup').get('timeout'))

    def _get_memory_out(self) -> str:
        """
        Gives the memory limit set to the experiments in this campaign.

        :return: The set memoru limit.
        """
        return str(self._dict_config.get('setup').get('memout'))

    def read_experiment_wares(self) -> 'ScalpelConfigurationBuilder':
        for xp_ware in self._dict_config['experiment-wares']:
            self._listener.start_experiment_ware()
            self._listener.log_data('name', xp_ware)
            self._listener.end_experiment_ware()
        return self


    def read_input_set(self) -> 'ScalpelConfigurationBuilder':
        self._listener.start_input_set()
        fmt = InputSetFormat.value_of(self._dict_config['input-set']['type'])
        name = self._dict_config['input-set']['name']
        self._listener.log_data('name', name)
        create_input_set_reader(fmt)(self._listener, self._dict_config['input-set']['path-list'][0])
        self._listener.end_input_set()

    def read_log_data(self) -> 'ScalpelConfigurationBuilder':
        self._main_file = self._dict_config['source']['path']

    def read_source(self) -> None:
        pass


def read_configuration(yaml_file: str, listener: CampaignParserListener) -> ScalpelConfiguration:
    """
    Loads Scalpel's configuration from the given YAML file.

    :param yaml_file: The path of the file to load the configuration from.
    :param listener: The listener to notify about the context of the campaign
                     while reading the configuration.

    :return: The read configuration.
    """
    with open(yaml_file, 'r') as yaml_stream:
        yaml = read_yaml(yaml_stream)
        builder = DictionaryScalpelConfigurationBuilder(yaml, listener)
        return builder.build()
