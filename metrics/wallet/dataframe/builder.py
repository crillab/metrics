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
from __future__ import annotations
from typing import Set, Callable, Any, List, Tuple

import jsonpickle
from pandas import DataFrame
from itertools import product

from metrics.core.model import Campaign
from metrics.core.constants import EXPERIMENT_CPU_TIME, SUCCESS_COL, INPUT_NAME, EXPERIMENT_INPUT, XP_WARE_NAME, \
    EXPERIMENT_XP_WARE
from metrics.scalpel import read_campaign, ScalpelConfiguration
from metrics.wallet.dataframe.dataframe import CampaignDataFrame
from metrics.wallet.figure.dynamic_figure import CactusPlotly, ScatterPlotly, BoxPlotly, CDFPlotly
from metrics.wallet.figure.static_figure import CactusMPL, ScatterMPL, BoxMPL, CDFMPL, StatTable, ContributionTable, \
    ErrorTable, PivotTable, Description, CDFMPL


class Analysis:

    def __init__(self, input_file: str = None, is_success: Callable[[Any], bool] = None, campaign: Campaign = None, campaign_df: CampaignDataFrame = None ):
        if campaign_df is None:
            self._input_file = input_file
            self._campaign = campaign
            self._is_success = (lambda x: x[EXPERIMENT_CPU_TIME] < self._campaign.timeout) if is_success is None else is_success
            if campaign is None:
                camp, config = self._make_campaign()
                self._campaign = camp
                suc = config.get_is_success()
                if suc is not None:
                    self._is_success = suc
            self._make_campaign_df()
        else:
            self._campaign_df = campaign_df

    @property
    def campaign_df(self):
        return self._campaign_df

    def _make_campaign(self) -> Tuple[Campaign, ScalpelConfiguration]:
        return read_campaign(self._input_file)

    def _make_campaign_df(self):
        self._campaign_df = CampaignDataFrameBuilder(self._campaign).build_from_campaign()
        self._complete_missing_experiments()

        self._campaign_df.data_frame[SUCCESS_COL] = self._campaign_df.data_frame.apply(self._is_success, axis=1)
        self._campaign_df.data_frame[EXPERIMENT_CPU_TIME] = self._campaign_df.data_frame.apply(lambda x: x[EXPERIMENT_CPU_TIME] if x[SUCCESS_COL] else self._campaign_df.campaign.timeout, axis=1)

    def _complete_missing_experiments(self):
        inputs = [i.name for i in self._campaign_df.campaign.input_set.inputs]
        xp_wares = [ew.name for ew in self._campaign_df.campaign.experiment_wares]
        theorical_xps = DataFrame(product(inputs, xp_wares), columns=['input', 'experiment_ware'])
        df = self._campaign_df._data_frame

        df['missing'] = False
        df = self._campaign_df._data_frame = self._campaign_df.data_frame.join(theorical_xps.set_index(['input', 'experiment_ware']), how='right', on=['input', 'experiment_ware'])
        df['missing'] = df['missing'].fillna(True)

    def map(self, new_col, function):
        df = self._campaign_df.data_frame
        df[new_col] = df.apply(function, axis=1)
        return self

    def sub_analysis(self, column, sub_set) -> Analysis:
        """
        Filters the dataframe in function of sub set of authorized values for a given column.
        @param column: column where  to keep the sub set of values.
        @param sub_set: the sub set of authorised values.
        @return: the filtered dataframe in a new instance of Analysis.
        """
        return Analysis(campaign_df=self._campaign_df.sub_data_frame(column, sub_set))

    def add_vbew(self, xp_ware_set=None, opti_col=EXPERIMENT_CPU_TIME, minimize=True, vbew_name='vbew', diff=0) -> Analysis:
        """
        Make a Virtual Best ExperimentWare.
        We get the best results of a sub set of experiment wares.
        For example, we can create the vbew of all current experimentwares based on the column cpu_time. A new
        experiment_ware "vbew" is created with best experiments (in term of cpu_time) of the xp_ware_set.
        @param xp_ware_set: we based this vbew on this subset of experimentwares.
        @param opti_col: the col we want to optimize.
        @param minimize: True if the min value is the optimal, False if it is the max value.
        @param vbew_name: name of the vbew.
        @return: a new instance of Analysis with the new vbew.
        """
        return Analysis(campaign_df=self._campaign_df.add_vbew(xp_ware_set, opti_col, minimize, vbew_name, diff))

    def groupby(self, column) -> List[Analysis]:
        """
        Makes a group by a given column.
        @param column: column where to applu the groupby.
        @return: a list of Analysis with each group.
        """
        return [
            Analysis(campaign_df=cdf) for cdf in self._campaign_df.groupby(column)
        ]

    def get_only_failed(self):
        return Analysis(campaign_df=self._campaign_df.get_only_failed())

    def get_only_success(self):
        return Analysis(campaign_df=self._campaign_df.get_only_success())

    def get_only_common_failed(self):
        return Analysis(campaign_df=self._campaign_df.get_only_common_failed())

    def get_only_common_success(self):
        return Analysis(campaign_df=self._campaign_df.get_only_common_success())

    def delete_common_failed(self):
        return Analysis(campaign_df=self._campaign_df.delete_common_failed())

    def delete_common_success(self):
        return Analysis(campaign_df=self._campaign_df.delete_common_success())

    def delete_input_when(self, f):
        return Analysis(campaign_df=self._campaign_df.delete_input_when(f))

    def describe(self, **kwargs: dict):
        return Description(self._campaign_df, **kwargs).get_description()

    def get_cactus_plot(self, dynamic: bool = False, **kwargs: dict):
        return (CactusPlotly(self._campaign_df, **kwargs) if dynamic else CactusMPL(self._campaign_df, **kwargs)).get_figure()

    def get_scatter_plot(self, dynamic: bool = False, **kwargs: dict):
        return (ScatterPlotly(self._campaign_df, **kwargs) if dynamic else ScatterMPL(self._campaign_df, **kwargs)).get_figure()

    def get_cdf(self, dynamic: bool = False, **kwargs: dict):
        return (CDFPlotly(self._campaign_df, **kwargs) if dynamic else CDFMPL(self._campaign_df, **kwargs)).get_figure()

    def get_box_plot(self, dynamic: bool = False, **kwargs: dict):
        return (BoxPlotly(self._campaign_df, **kwargs) if dynamic else BoxMPL(self._campaign_df, **kwargs)).get_figure()

    def get_stat_table(self, **kwargs: dict):
        return StatTable(self._campaign_df, **kwargs).get_figure()

    def get_contribution_table(self, **kwargs: dict):
        return ContributionTable(self._campaign_df, **kwargs).get_figure()

    def get_error_table(self, **kwargs: dict):
        return ErrorTable(self._campaign_df, **kwargs).get_figure()

    def get_pivot_table(self, **kwargs: dict):
        return PivotTable(self._campaign_df, **kwargs).get_figure()

    def export(self):
        return jsonpickle.encode(self)


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
            .join(inputs_df.set_index(INPUT_NAME), on=EXPERIMENT_INPUT, lsuffix='_experiment', rsuffix='_input', how='inner') \
            .join(experiment_wares_df.set_index(XP_WARE_NAME),
                  on=EXPERIMENT_XP_WARE, lsuffix='_experiment', rsuffix='_xpware', how='inner'
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
