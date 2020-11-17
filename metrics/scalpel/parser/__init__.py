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
This package provides the modules allowing to parse files so as to retrieve
the experimental data collected during a campaign.
"""


from pydoc import locate

from metrics.scalpel import CampaignParserListener
from metrics.scalpel.config import CampaignFormat, ScalpelConfiguration
from metrics.scalpel.parser.campaign import *


def create_parser(configuration: ScalpelConfiguration, listener: CampaignParserListener) -> CampaignParser:
    """
    Creates the most appropriate parser to use to parse the campaign described
    in the given configuration.

    :param configuration: The configuration describing the campaign to parse.
    :param listener: The listener to notify while parsing.

    :return: The parser to use to parse the campaign.
    """
    # If the user has written their own parser, this parser is used.
    custom_parser = configuration.get_custom_parser()
    if custom_parser is not None:
        return locate(custom_parser)(configuration, listener)

    # Otherwise, a default parser is chosen w.r.t. the campaign's format.
    campaign_format = configuration.get_format()

    if campaign_format in (CampaignFormat.CSV, CampaignFormat.CSV2, CampaignFormat.TSV):
        return CsvCampaignParser(listener, configuration.get_file_name_meta(), configuration.get_csv_configuration())

    if campaign_format in (CampaignFormat.REVERSE_CSV, CampaignFormat.REVERSE_CSV2, CampaignFormat.REVERSE_TSV):
        return ReverseCsvCampaignParser(listener, configuration.get_file_name_meta(), configuration.get_csv_configuration())

    if campaign_format == CampaignFormat.EVALUATION:
        return EvaluationCampaignParser(listener, configuration.get_file_name_meta())

    if campaign_format == CampaignFormat.SINGLE_EXPERIMENT_LOG_FILE:
        return DirectoryCampaignParser(SingleFileExplorationStrategy(listener, configuration))

    if campaign_format == CampaignFormat.MULTIPLE_EXPERIMENT_LOG_FILES:
        return DirectoryCampaignParser(NameBasedFileExplorationStrategy(listener, configuration))

    if campaign_format == CampaignFormat.EXPERIMENT_DIRECTORY:
        return DirectoryCampaignParser(AllFilesExplorationStrategy(listener, configuration))

    raise ValueError(f'Unrecognized input format: {campaign_format}')
