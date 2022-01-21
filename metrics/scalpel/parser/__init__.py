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
This package provides the modules allowing to parse files to retrieve the
experimental data collected during a campaign.
"""


from metrics.scalpel.parser.campaign import CampaignParser
from metrics.scalpel.parser.campaign import CsvCampaignParser, ReverseCsvCampaignParser
from metrics.scalpel.parser.campaign import EvaluationCampaignParser
from metrics.scalpel.parser.campaign import DirectoryCampaignParser
from metrics.scalpel.parser.campaign import AllFilesExplorationStrategy, \
    NameBasedFileExplorationStrategy, SingleFileExplorationStrategy

from metrics.scalpel import CampaignParserListener

from metrics.scalpel.config import CampaignFormat, ScalpelConfiguration


def create_parser(configuration: ScalpelConfiguration,
                  listener: CampaignParserListener) -> CampaignParser:
    """
    Creates the most appropriate parser to use to parse the campaign described
    in the given configuration.

    :param configuration: The configuration describing the campaign to parse.
    :param listener: The listener to notify while parsing.

    :return: The parser to use to parse the campaign.

    :raises ValueError: If an appropriate parser could not be instantiated.
    """
    # If the user has written their own parser, this parser is instantiated.
    custom_parser = configuration.get_custom_parser()
    if custom_parser is not None:
        return custom_parser(listener, configuration)

    # Otherwise, a default parser is chosen w.r.t. the campaign's format.
    if configuration.get_format() == CampaignFormat.EVALUATION:
        return EvaluationCampaignParser(listener, configuration.get_file_name_meta())

    if configuration.get_format().is_csv():
        return CsvCampaignParser(listener, configuration.get_file_name_meta(),
                                 configuration.get_csv_configuration())

    if configuration.get_format().is_reverse_csv():
        return ReverseCsvCampaignParser(listener, configuration.get_file_name_meta(),
                                        configuration.get_csv_configuration())

    if configuration.get_format() == CampaignFormat.SINGLE_EXPERIMENT_LOG_FILE:
        return DirectoryCampaignParser(configuration,
                                       SingleFileExplorationStrategy(listener, configuration))

    if configuration.get_format() == CampaignFormat.MULTIPLE_EXPERIMENT_LOG_FILES:
        return DirectoryCampaignParser(configuration,
                                       NameBasedFileExplorationStrategy(listener, configuration))

    if configuration.get_format() == CampaignFormat.EXPERIMENT_DIRECTORY:
        return DirectoryCampaignParser(configuration,
                                       AllFilesExplorationStrategy(listener, configuration))

    raise ValueError(f'Unrecognized campaign format: {configuration.get_format()}')
