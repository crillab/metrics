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
Metrics-Scalpel (sCAlPEL - extraCting dAta of exPeriments from softwarE Logs)
provides tools for extracting data produced during software experiments to
analyze this data later on with, e.g., Metrics-Wallet.
"""


from typing import Any, Iterable, Optional, Tuple

from jsonpickle import decode as load_json

from metrics.core.model import Campaign

from metrics.scalpel.listener import CampaignParserListener

from metrics.scalpel.config import read_configuration, ScalpelConfiguration
from metrics.scalpel.parser import create_parser
from metrics.scalpel.utils import configure_logger


def read_campaign(input_file: str,
                  log_level: str = 'WARNING') -> Tuple[Campaign, Optional[ScalpelConfiguration]]:
    """
    Reads the data about a campaign based on the given input file.

    :param input_file: The input file describing the campaign.
    :param log_level: The minimum level for the events to log while parsing the campaign.

    :return: The read campaign and the configuration of this campaign, if any.

    :raises ValueError: If the input file does not have a recognized format.
    """
    if input_file.lower().endswith('.yml') or input_file.lower().endswith('.yaml'):
        return read_yaml(input_file, log_level)

    if input_file.lower().endswith('.json'):
        return read_json(input_file), None

    raise ValueError(f'Unrecognized campaign format for file "{input_file}"')


def read_yaml(yaml_configuration: str,
              log_level: str = 'WARNING') -> Tuple[Campaign, ScalpelConfiguration]:
    """
    Reads the data about a campaign following the configuration described in
    the given YAML file.

    :param yaml_configuration: The path of the YAML file describing Scalpel's
                               configuration.
    :param log_level: The minimum level for the events to log while parsing the campaign.

    :return: The read campaign and the configuration of this campaign.
    """
    configure_logger(log_level)
    parser_listener = CampaignParserListener()
    configuration = read_configuration(yaml_configuration, parser_listener)
    campaign_parser = create_parser(configuration, parser_listener)
    for file in configuration.get_path():
        campaign_parser.parse_file(file)
    return parser_listener.get_campaign(), configuration


def read_json(json_file: str) -> Campaign:
    """
    Reads a campaign that has been serialized in a JSON file.

    :param json_file: The path of the JSON file to read the campaign from.

    :return: The read campaign.
    """
    with open(json_file, 'r', encoding='utf-8') as json_campaign:
        return load_json(json_campaign.read())


def read_object(yaml_configuration: str, campaign: Iterable[Any],
                log_level: str = 'WARNING') -> Tuple[Campaign, ScalpelConfiguration]:
    """
    Reads the data stored in the given iterable object following the
    configuration described in the given YAML file.

    :param yaml_configuration: The path of the YAML file describing Scalpel's configuration.
    :param campaign: The object to iterate over to get the data about the campaign.
                     Each element encountered during the iteration is supposed to represent
                     an experiment, and must define an "items()" method returning a set of
                     key-value pairs (such as dictionaries or rows in a data-frame,
                     for instance).
    :param log_level: The minimum level for the events to log while parsing the campaign.

    :return: The read campaign and the configuration of this campaign.
    """
    configure_logger(log_level)
    parser_listener = CampaignParserListener()
    configuration = read_configuration(yaml_configuration, parser_listener)
    for experiment in campaign:
        parser_listener.start_experiment()
        for key, value in experiment.items():
            parser_listener.log_data(key, value)
        parser_listener.end_experiment()
    return parser_listener.get_campaign(), configuration
