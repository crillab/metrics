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
Metrics-Scalpel (sCAlPEL - extraCting dAta of exPeriments from softwarE Logs)
provides tools for extracting data produced during software experiments so as
to analyze this data later on, e.g., using Metrics-Wallet or Metrics-Studio.
"""


from typing import Any, Iterable, Optional, Tuple

from jsonpickle import decode as load_json

from metrics.core.model import Campaign

from metrics.scalpel.config import read_configuration, ScalpelConfiguration
from metrics.scalpel.listener import CampaignParserListener
from metrics.scalpel.parser import create_parser


def read_campaign(input_file: str) -> Tuple[Campaign, Optional[ScalpelConfiguration]]:
    """
    Reads the data about a campaign from the given input file.

    :param input_file: The input file describing the campaign.

    :return: The read campaign and the configuration of this campaign, if any.

    :raises ValueError: If the input file does not have a recognized format.
    """
    if input_file.endswith('.yml') or input_file.endswith('.yaml'):
        return read_yaml(input_file)

    if input_file.endswith('.json'):
        return read_json(input_file), None

    raise ValueError(f'Unrecognized campaign format for file "{input_file}"')


def read_yaml(yaml_configuration: str) -> Tuple[Campaign, ScalpelConfiguration]:
    """
    Reads the data about a campaign following the configuration described in
    the given YAML file.

    :param yaml_configuration: The path of the YAML file describing Scalpel's
                               configuration.

    :return: The read campaign and the configuration of this campaign.
    """
    parser_listener = CampaignParserListener()
    configuration = read_configuration(yaml_configuration, parser_listener)
    campaign_parser = create_parser(configuration, parser_listener)
    for file in configuration.get_main_file():
        campaign_parser.parse_file(file)
    return parser_listener.get_campaign(), configuration


def read_json(json_file: str) -> Campaign:
    """
    Reads a campaign that has been serialized in a JSON file.

    :param json_file: The path of the JSON file to read the campaign from.

    :return: The read campaign.
    """
    with open(json_file, 'r') as json_campaign:
        return load_json(json_campaign.read())


def read_object(yaml_configuration: str, campaign: Iterable[Any]) -> Tuple[Campaign, ScalpelConfiguration]:
    """
    Reads the data stored in the given iterable object following the
    configuration described in the given YAML file.

    :param yaml_configuration: The path of the YAML file describing Scalpel's
                               configuration.
    :param campaign: The object to iterate over so as to get the data about the
                     campaign.
                     Each element encountered during the iteration is supposed to
                     represent an experiment, and must define an "items()" method
                     returning a set of key-value pairs (such as dictionaries or
                     rows in a data-frame, for instance).

    :return: The read campaign and the configuration of this campaign.
    """
    parser_listener = CampaignParserListener()
    configuration = read_configuration(yaml_configuration, parser_listener)
    for experiment in campaign:
        parser_listener.start_experiment()
        for key, value in experiment.items():
            parser_listener.log_data(key, value)
        parser_listener.end_experiment()
    return parser_listener.get_campaign(), configuration
