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
import jsonpickle

from metrics.core.model import Campaign
from metrics.wallet.dataframe.builder import Analysis
from metrics.wallet.dataframe.dataframe import CampaignDataFrame


def import_campaigns(jsons) -> Campaign:
    campaign = import_campaign(jsons[0])

    for i in range(1, len(jsons)):
        tmp = import_campaign(jsons[i])

        #campaign.experiment_wares.extend(tmp.experiment_wares)
        campaign.experiments.extend(tmp.experiments)
        campaign.input_set.inputs.extend(tmp.input_set.inputs)

    return campaign

def import_campaign(json) -> Campaign:
    return jsonpickle.decode(json)


def import_campaign_data_frame(json) -> CampaignDataFrame:
    return jsonpickle.decode(json)


def import_analysis(json) -> Analysis:
    return jsonpickle.decode(json)