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
This package provides the modules for setting up Scalpel, in particular to configure
how it can extract relevant data from the files of the campaign to parse.
"""


from yaml import safe_load as load_yaml

from metrics.scalpel import CampaignParserListener

from metrics.scalpel.config.config import FileNameMetaConfiguration
from metrics.scalpel.config.config import ScalpelConfiguration
from metrics.scalpel.config.config import ScalpelConfigurationLoader

from metrics.scalpel.config.format import CampaignFormat
from metrics.scalpel.config.format import OutputFormat

from metrics.scalpel.config.wrapper import DictScalpelConfigurationWrapper
from metrics.scalpel.config.wrapper import IScalpelConfigurationWrapper


def read_configuration(yaml_file: str, listener: CampaignParserListener) -> ScalpelConfiguration:
    """
    Loads Scalpel's configuration from the given YAML file.

    :param yaml_file: The path of the file to load the configuration from.
    :param listener: The listener to notify about the context of the campaign
                     while reading the configuration.

    :return: The read configuration.
    """
    with open(yaml_file, 'r', encoding='utf-8') as yaml_stream:
        yaml_dict = load_yaml(yaml_stream)
        return load_configuration(DictScalpelConfigurationWrapper(yaml_dict), listener)


def load_configuration(configuration: IScalpelConfigurationWrapper,
                       listener: CampaignParserListener) -> ScalpelConfiguration:
    """
    Loads Scalpel's configuration using the given wrapper.

    :param configuration: The wrapper of Scalpel's configuration.
    :param listener: The listener to notify about the context of the campaign
                     while loading the configuration.

    :return: The loaded configuration.
    """
    loader = ScalpelConfigurationLoader(configuration, listener)
    return loader.load()
