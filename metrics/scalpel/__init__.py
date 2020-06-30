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


from metrics.core.model import Model

from metrics.scalpel.config import read_configuration
from metrics.scalpel.listener import CampaignParserListener
from metrics.scalpel.parser import create_parser, GenericJsonCampaignParser


def read_campaign(input_file: str, from_json: bool = True) -> Model:
    """
    Reads the data about a campaign from the given input file.

    :param input_file: The input file describing the campaign.
    :param from_json: Whether the input file is JSON.

    :return: The read campaign.
    """
    return read_json(input_file) if from_json else read_yaml(input_file)


def read_yaml(yaml_configuration: str) -> Model:
    """
    Reads the data about a campaign following the configuration described in
    the given YAML file.

    :param yaml_configuration: The path of the YAML file describing Scalpel's
           configuration.

    :return: The read campaign.
    """
    campaign_parser_listener = CampaignParserListener()
    configuration = read_configuration(yaml_configuration, campaign_parser_listener)
    campaign_parser = create_parser(configuration, campaign_parser_listener)
    campaign_parser.parse_file(configuration.get_main_file())
    return campaign_parser_listener.get_campaign()


def read_json(json_file: str) -> Model:
    """
    Reads the data about a campaign from the given JSON file.
    This file is supposed to be the serialized form of a campaign (reading
    any JSON file is not supported).

    :param json_file: The path of the JSON file to read the campaign from.

    :return: The read campaign.
    """
    campaign_parser_listener = CampaignParserListener()
    campaign_parser = GenericJsonCampaignParser(campaign_parser_listener)
    campaign_parser.parse_file(json_file)
    return campaign_parser_listener.get_campaign()
