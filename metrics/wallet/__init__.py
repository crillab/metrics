# ##############################################################################
#  Wallet - A Metrics Module                                                   #
#  Copyright (c) 2019-2020 - Univ Artois & CNRS, Exakis Nelite                 #
#  --------------------------------------------------------------------------  #
#  mETRICS - rEproducible sofTware peRformance analysIs in perfeCt Simplicity  #
#  wALLET - Automated tooL for expLoiting Experimental resulTs                 #
#                                                                              #
#                                                                              #
#  This program is free software: you can redistribute it and/or modify it     #
#  under the terms of the GNU Lesser General Public License as published by    #
#  the Free Software Foundation, either version 3 of the License, or (at your  #
#  option) any later version.                                                  #
#                                                                              #
#  This program is distributed in the hope that it will be useful, but         #
#  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY  #
#  or FITNESS FOR A PARTICULAR PURPOSE.                                        #
#  See the GNU General Public License for more details.                        #
#                                                                              #
#  You should have received a copy of the GNU Lesser General Public License    #
#  along with this program.                                                    #
#  If not, see <https://www.gnu.org/licenses/>.                                #
# ##############################################################################
import os
from pathlib import Path

from metrics.core.model import Campaign
from metrics.wallet.dataframe.builder import Analysis
from metrics.wallet.dataframe.dataframe import CampaignDataFrame
from metrics.wallet.figure.static_figure import LINE_STYLES, DEFAULT_COLORS

import pickle


def import_campaigns(jsons) -> Campaign:
    campaign = import_campaign(jsons[0])

    for i in range(1, len(jsons)):
        tmp = import_campaign(jsons[i])

        campaign.experiments.extend(tmp.experiments)
        campaign.input_set.inputs.extend(tmp.input_set.inputs)

    return campaign


def get_cache_or_parse(input_file):

    if os.path.isfile('.cache'):
        with open('.cache', 'rb') as file:
            return import_analysis_from_file(file)
    else:
        with open('.cache', 'wb') as file:
            analysis = Analysis(input_file=input_file)
            analysis.export(file=file)
            return analysis


def import_campaign(str) -> Campaign:
    return pickle.loads(str)


def import_campaign_from_file(file):
    return pickle.load(file)


def import_campaign_data_frame(str) -> CampaignDataFrame:
    return pickle.loads(str)


def import_campaign_data_frame_from_file(file):
    return pickle.load(file)


def import_analysis(str) -> Analysis:
    return pickle.loads(str)


def import_analysis_from_file(file):
    return pickle.load(file)
