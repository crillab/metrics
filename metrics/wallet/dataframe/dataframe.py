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
This module provides the campaign dataframe object.
This module uses the DataFrame object pandas library.
"""

from __future__ import annotations

from enum import Enum
from typing import List

import pandas as pd

from metrics.wallet.dataframe.builder import *


class CampaignDFFilter(Enum):
    """
    This enumeration provides all the needed operations that we can apply to our dataframe.
    """
    ONLY_TIMEOUT = (lambda c, df:   df[df['cpu_time'] >= c.timeout])
    ONLY_SOLVED = (lambda c, df:    df[df['cpu_time'] < c.timeout])
    ONLY_COMMON_TIMEOUT = (lambda c, df:    df[~df.input.isin(CampaignDFFilter.ONLY_SOLVED(c, df).input)])
    ONLY_COMMON_SOLVED = (lambda c, df:     df[~df.input.isin(CampaignDFFilter.ONLY_TIMEOUT(c, df).input)])
    DELETE_COMMON_TIMEOUT = (lambda c, df:  df[df.input.isin(CampaignDFFilter.ONLY_SOLVED(c, df).input)])
    DELETE_COMMON_SOLVED = (lambda c, df:   df[df.input.isin(CampaignDFFilter.ONLY_TIMEOUT(c, df).input)])

    def __init__(self, df_filter):
        """
        Creates a new filter for the campaign.
        @param df_filter: the filter we can apply to a campaign dataframe.
        """
        self._df_filter = df_filter

    def __call__(self, campaign, data_frame):
        """
        At calls we apply the filter on campaign and dataframe.
        @param campaign: the campaign.
        @param data_frame: the dataframe corresponding to the dataframe.
        @return: the filtered dataframe.
        """
        return self._df_filter(campaign, data_frame)


class CampaignDataFrame:
    """
    This object encapsulate a dataframe (pandas DataFrame) that corresponds to a campaign.
    This encapsulation permits to apply many operations.
    """

    def __init__(self, campaign_df_builder: CampaignDataFrameBuilder, data_frame: pd.DataFrame, name: str):
        """
        Creates a CampaignDataFrame.
        @param campaign_df_builder: the builder used to build this campaign.
        @param data_frame: the dataframe builded by the builder.
        @param name: the name of this camapaign dataframe.
        """
        self._campaign_df_builder = campaign_df_builder
        self._campaign = campaign_df_builder.campaign
        self._data_frame = data_frame
        self._xp_ware_names = list(data_frame.experiment_ware.unique())
        self._name = name

    @property
    def data_frame(self) -> pd.DataFrame:
        """

        @return: the dataframe corresponding to the campaign.
        """
        return self._data_frame

    @property
    def campaign(self) -> pd.DataFrame:
        """

        @return: the campaign.
        """
        return self._campaign

    @property
    def name(self) -> str:
        """

        @return: the name of the current campaign dataframe.
        """
        return self._name

    @property
    def xp_ware_names(self) -> List[str]:
        """

        @return: the experimentware names of the dataframe.
        """
        return self._xp_ware_names

    def filter_by(self, filters: List[CampaignDFFilter]):
        """
        Permits to filter the current dataframe by the list of provided filters.
        We can apply this only on a subset of experimentwares.
        @param filters: filters to apply.
        @return: a new instance of CampaignDataFrame with the filtered dataframe inside.
        """
        df = self._data_frame

        for f in filters:
            df = f(self._campaign, df)

        return self.build_data_frame(df)

    def sub_data_frame(self, column, sub_set) -> CampaignDataFrame:
        """
        Filters the dataframe in function of sub set of authorized values for a given column.
        @param column: column where  to keep the sub set of values.
        @param sub_set: the sub set of authorised values.
        @return: the filtered dataframe in a new instance of CampaignDataFrame.
        """
        df = self._data_frame[self._data_frame[column].isin(sub_set)]
        return self.build_data_frame(df)

    def add_vbew(self, xp_ware_set, opti_col, minimize=True, vbew_name='vbew') -> CampaignDataFrame:
        """
        Make a Virtual Best ExperimentWare.
        We get the best results of a sub set of experiment wares.
        For example, we can create the vbew of all current experimentwares based on the column cpu_time. A new
        experiment_ware "vbew" is created with best experiments (in term of cpu_time) of the xp_ware_set.
        @param xp_ware_set: we based this vbew on this subset of experimentwares.
        @param opti_col: the col we want to optimize.
        @param minimize: True if the min value is the optimal, False if it is the max value.
        @param vbew_name: name of the vbew.
        @return: a new instance of CampaignDataFrame with the new vbew.
        """
        df = self._data_frame
        df = df[df.experiment_ware != 'vbs']

        df_vbs = df[df['experiment_ware'].isin(xp_ware_set)]
        df_vbs = df_vbs.sort_values(by=opti_col, ascending=minimize).drop_duplicates(['input'])\
            .assign(experiment_ware=lambda x: vbew_name)
        df = pd.concat([df, df_vbs], ignore_index=True)

        return self.build_data_frame(df)

    def groupby(self, column) -> List[CampaignDataFrame]:
        """
        Makes a group by a given column.
        @param column: column where to applu the groupby.
        @return: a list of CampaignDataFrame with each group.
        """
        gb = self._data_frame.groupby(column)

        return [
            self.build_data_frame(group, name=name) for name, group in gb
        ]

    def build_data_frame(self, df, name: str = None):
        """
        Call the original builder to rebuild this campaign with its filtered dataframe.
        @param df: filtered dataframe.
        @param name: name of the campaign dataframe.
        @return: a new instance of CampaignDataFrame with the filtered dataframe.
        """
        return self._campaign_df_builder.build_from_data_frame(df, name=name)
