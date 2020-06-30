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

"""
This module provides a simple class corresponding to the builder of the dataframe linked to a campaign.
"""
from typing import Set, Callable, Any

from pandas import DataFrame

from metrics.core.model import Campaign
from metrics.scalpel import read_yaml
from metrics.wallet.dataframe.dataframe import CampaignDataFrame


class Analysis:

    def __init__(self, input_file: str, is_success: Callable[[Any], bool] = None):
        self._input_file = input_file
        self._campaign = self._make_campaign()
        self._is_success = (lambda x: x['cpu_time'] < self._campaign.timeout) if is_success is None else is_success
        self._campaign_df = self._make_campaign_df()

    @property
    def campaign_df(self):
        return self._campaign_df

    def _make_campaign(self) -> Campaign:
        return read_yaml(self._input_file)

    def _make_campaign_df(self):
        campaign_df = CampaignDataFrameBuilder(self._campaign).build_from_campaign()
        campaign_df.data_frame['success'] = campaign_df.data_frame.apply(self._is_success, axis=1)
        return campaign_df


class CampaignDataFrameBuilder:
    """
    This builder permits to make a campaign dataframe.
    """

    def __init__(self, campaign: Campaign):
        """
        Creates a campaign dataframe.
        @param campaign: the campaign to build as a campaign
        """
        self._campaign = campaign

    @property
    def campaign(self):
        """

        @return: the campaign associated to this builder.
        """
        return self._campaign

    def build_from_campaign(self) -> CampaignDataFrame:
        """
        Builds a campaign dataframe directly from the original campaign.
        @return: the builded campaign dataframe.
        """
        experiment_wares_df = self._make_experiment_wares_df()
        inputs_df = self._make_inputs_df()
        experiments_df = self._make_experiments_df()

        campaign_df = experiments_df \
            .join(inputs_df.set_index('path'), on='input', lsuffix='_experiment', rsuffix='_input', how='inner') \
            .join(experiment_wares_df.set_index('name'),
                  on='experiment_ware', lsuffix='_experiment', rsuffix='_xpware', how='inner'
                  )

        return self.build_from_data_frame(campaign_df, self._campaign.name)

    def build_from_data_frame(self, campaign_df: DataFrame, name: str = None, vbew_names: Set[str] = None) -> CampaignDataFrame:
        """
        Builds a campaign dataframe directly from a pandas dataframe. It must corresponds to the original dataframe
        with some modifications but with necessary columns.
        @param campaign_df: a pandas dataframe.
        @param name: the name corresponding to the current dataframe.
        @return: the builded campaign dataframe.
        """
        return CampaignDataFrame(self, campaign_df, name or self._campaign.name, vbew_names or set())

    def _make_experiment_wares_df(self) -> DataFrame:
        """
        Makes the data frame composed of experiment wares.
        @return: the data frame composed of experiment wares.
        """
        return DataFrame([ware.__dict__ for ware in self._campaign.experiment_wares])

    def _make_inputs_df(self) -> DataFrame:
        """
        Makes the data frame composed of inputs.
        @return: the data frame composed of inputs.
        """
        return DataFrame([input.__dict__ for input in self._campaign.input_set.inputs])

    def _make_experiments_df(self) -> DataFrame:
        """
        Makes the data frame composed of experiments.
        @return: the data frame composed of experiments.
        """
        return DataFrame([xp.__dict__ for xp in self._campaign.experiments])
