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

from metrics.wallet.analysis import *


class CampaignDFFilter(Enum):
    """
    This enumeration provides all the needed operations that we can apply to our dataframe.
    """
    ONLY_TIMEOUT = (lambda c, df:   df[~df[SUCCESS_COL]])
    ONLY_SOLVED = (lambda c, df:    df[df[SUCCESS_COL]])
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


def _vbew_agg(df, opti_col, minimize, diff):
    df = df.sort_values(opti_col, ascending=minimize)

    df['contributor'] = df['experiment_ware'].values[0]

    i1 = df[opti_col].values[0]
    i2 = df[opti_col].values[1]

    if i1 == i2:
        return df.iloc[0] if diff == 0 else None

    if i1 == 0:
        return df.iloc[0]

    return df.iloc[0] if (i2 - i1) / i1 >= diff else None


class CampaignDataFrame:
    """
    This object encapsulate a dataframe (pandas DataFrame) that corresponds to a campaign.
    This encapsulation permits to apply many operations.
    """

    def __init__(self, campaign_df_builder: CampaignDataFrameBuilder, data_frame: pd.DataFrame, name: str, vbew_names: Set[str]):
        """
        Creates a CampaignDataFrame.
        @param campaign_df_builder: the builder used to build this campaign.
        @param data_frame: the dataframe builded by the builder.
        @param name: the name of this camapaign dataframe.
        """
        self._campaign_df_builder = campaign_df_builder
        self._campaign = campaign_df_builder.campaign
        self._data_frame = data_frame
        self._name = name
        self._vbew_names = vbew_names

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
    def experiment_wares(self) -> List[str]:
        """

        @return: the experimentware names of the dataframe.
        """
        return self.data_frame[EXPERIMENT_XP_WARE].unique()

    @property
    def inputs(self) -> List[str]:
        """

        @return: the input names of the dataframe.
        """
        return self.data_frame[EXPERIMENT_INPUT].unique()

    @property
    def vbew_names(self) -> Set[str]:
        """

        @return: the vbew names of the dataframe.
        """
        return self._vbew_names

    def _filter_by(self, filters: List[CampaignDFFilter]):
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

    def get_only_failed(self):
        return self._filter_by([CampaignDFFilter.ONLY_TIMEOUT])

    def get_only_success(self):
        return self._filter_by([CampaignDFFilter.ONLY_SOLVED])

    def get_only_common_failed(self):
        return self._filter_by([CampaignDFFilter.ONLY_COMMON_TIMEOUT])

    def get_only_common_success(self):
        return self._filter_by([CampaignDFFilter.ONLY_COMMON_SOLVED])

    def delete_common_failed(self):
        return self._filter_by([CampaignDFFilter.DELETE_COMMON_TIMEOUT])

    def delete_common_success(self):
        return self._filter_by([CampaignDFFilter.DELETE_COMMON_SOLVED])

    def sub_data_frame(self, column, sub_set) -> CampaignDataFrame:
        """
        Filters the dataframe in function of sub set of authorized values for a given column.
        @param column: column where  to keep the sub set of values.
        @param sub_set: the sub set of authorised values.
        @return: the filtered dataframe in a new instance of CampaignDataFrame.
        """
        df = self._data_frame[self._data_frame[column].isin(sub_set)]
        return self.build_data_frame(df)

    def add_vbew(self, xp_ware_set=None, opti_col=EXPERIMENT_CPU_TIME, minimize=True, vbew_name='vbew', diff=0) -> CampaignDataFrame:
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
        if xp_ware_set is None:
            xp_ware_set = self.xp_ware_names

        df_vbs = df[df[EXPERIMENT_XP_WARE].isin(xp_ware_set)]

        df_vbs = df_vbs.groupby(EXPERIMENT_INPUT).apply(lambda x: _vbew_agg(x, opti_col, minimize, diff)).dropna(how='all')\
            .assign(experiment_ware=lambda x: vbew_name)

        df = df[df[EXPERIMENT_INPUT].isin(df_vbs[EXPERIMENT_INPUT])]
        df = pd.concat([df, df_vbs], ignore_index=True)

        self._vbew_names.add(vbew_name)

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

    def delete_input_when(self, f):
        df = self._data_frame.copy()
        df['f_res'] = df.apply(f, axis=1)
        input_to_del = df.groupby('input')['f_res'].aggregate(all)

        df = self._data_frame
        df = df[~df['input'].isin(input_to_del[input_to_del].index)]

        return self.build_data_frame(df, self._name)

    def build_data_frame(self, df, name: str = None):
        """
        Call the original builder to rebuild this campaign with its filtered dataframe.
        @param df: filtered dataframe.
        @param name: name of the campaign dataframe.
        @return: a new instance of CampaignDataFrame with the filtered dataframe.
        """
        return self._campaign_df_builder.build_from_data_frame(df, name=name, vbew_names=self._vbew_names)

    def export(self):
        return jsonpickle.encode(self)
