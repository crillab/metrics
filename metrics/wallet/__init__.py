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
import urllib
from pathlib import Path

from metrics.core.model import Campaign
from metrics.wallet.dataframe.builder import Analysis
from metrics.wallet.dataframe.dataframe import CampaignDataFrame
from metrics.wallet.figure.static_figure import LINE_STYLES, DEFAULT_COLORS

import jsonpickle
import jsonpickle.ext.pandas as jsonpickle_pd

jsonpickle_pd.register_handlers()


def import_campaigns(jsons) -> Campaign:
    campaign = import_campaign(jsons[0])

    for i in range(1, len(jsons)):
        tmp = import_campaign(jsons[i])

        campaign.experiments.extend(tmp.experiments)
        campaign.input_set.inputs.extend(tmp.input_set.inputs)

    return campaign


def import_from_api_and_store(url, path):
    file = Path(path)

    if file.exists():
        content = file.read_text()
    else:
        with urllib.request.urlopen(url) as url:
            content = url.read().decode()
            file.write_text(content)

    return import_campaign(content)


def import_campaign(content) -> Campaign:
    return jsonpickle.decode(content)


def import_campaign_data_frame(content) -> CampaignDataFrame:
    return jsonpickle.decode(content)


def import_analysis(content) -> Analysis:
    return jsonpickle.decode(content)
