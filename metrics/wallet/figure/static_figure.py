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
from typing import List

import matplotlib.pyplot as plt
import pandas as pd

from metrics.wallet.dataframe.dataframe import CampaignDFFilter, CampaignDataFrame
from metrics.wallet.figure.abstract_figure import Figure, CactusPlot, BoxPlot, ScatterPlot

LINE_STYLES = ['-', ':', '-.', '--']
"""
Corresponds to a sample of existing line styles for matplotlib.
"""


class StatTable(Figure):
    """
    Creation of a stat table representing main statistics for a campaign.
    """

    def get_figure(self):
        """

        @return: the figure.
        """
        return self.get_data_frame().T

    def get_data_frame(self):
        df_stat = pd.DataFrame(index=self.campaign_df.xp_ware_names)

        only_solved_df = self.campaign_df.filter_by([
            CampaignDFFilter.ONLY_SOLVED,
        ]).data_frame

        no_common_failed = self.campaign_df.filter_by([
            CampaignDFFilter.DELETE_COMMON_TIMEOUT,
        ]).data_frame

        common_inputs = self.campaign_df.filter_by([
            CampaignDFFilter.ONLY_COMMON_SOLVED,
        ]).data_frame

        no_common_solved_no_out = self.campaign_df.filter_by([
            CampaignDFFilter.DELETE_COMMON_SOLVED,
            CampaignDFFilter.ONLY_SOLVED,
        ]).data_frame

        df_stat['count'] = only_solved_df.groupby('experiment_ware')['cpu_time'].count()
        df_stat['sum'] = no_common_failed.groupby('experiment_ware')['cpu_time'].sum()
        df_stat['common_count'] = common_inputs.groupby('experiment_ware')['cpu_time'].count()
        df_stat['common_sum'] = common_inputs.groupby('experiment_ware')['cpu_time'].sum()
        df_stat['uncommon_count'] = no_common_solved_no_out.groupby('experiment_ware')['cpu_time'].count()
        df_stat['total'] = len(self.campaign_df.data_frame['input'].unique())

        df_stat = df_stat.sort_values(['count', 'sum'], ascending=[False, True])

        return df_stat.fillna(0).astype(int)


def contribution_agg(slice: pd.DataFrame, to: float):
    slice = slice.sort_values(by='cpu_time')
    first = slice.iloc[0]
    second = slice.iloc[1]

    if first['cpu_time'] < to:
        return pd.Series([first['experiment_ware'], first['cpu_time'], second['cpu_time'] >= to],
                         index=['first', 'cpu_time', 'unique'])

    return pd.Series([None, None, False], index=['first', 'cpu_time', 'unique'])


class ContributionTable(Figure):
    """
    Creation of a table representing the different contributions of each solver.
    """

    def __init__(self, campaign_df: CampaignDataFrame, vbew_deltas: List[float]):
        super().__init__(campaign_df)
        self.vbew_deltas = vbew_deltas

    def get_figure(self):
        """

        @return: the figure.
        """
        return self.get_data_frame()

    def get_data_frame(self):
        contrib_raw = self.campaign_df.data_frame.groupby('input').apply(
            lambda x: contribution_agg(x, self.campaign_df.campaign.timeout))
        contrib = pd.DataFrame()

        contrib['vbew_simple'] = contrib_raw.groupby('first').cpu_time.count()

        for delta in self.vbew_deltas:
            sub = contrib_raw[contrib_raw.cpu_time > delta]
            contrib[f'vbew > {delta}'] = sub.groupby('first').cpu_time.count()

        contrib['contribution'] = contrib_raw.groupby('first').unique.sum()

        return contrib.fillna(0).astype(int).sort_values(['vbew_simple', 'contribution'], ascending=[False, False])


class CactusMPL(CactusPlot):
    """
    Creation of a static cactus plot.
    """

    def get_figure(self):
        """

        @return: the figure.
        """
        df = self.get_data_frame()

        fig, ax = plt.subplots()
        ax.set_title(self.get_title(), **self._font)
        ax.set_xlabel(self.get_x_axis_name(), **self._font)
        ax.set_ylabel(self.get_y_axis_name(), **self._font)

        styles = [self.style_map.get(x) for x in df.columns] if self.style_map else None

        kwargs = [
            {
                'color': self.color_map.get(x) if self.color_map else None,
                'linewidth': 3 if x in self.campaign_df.vbew_names else 1
            } for x in df.columns
        ]

        for i, col in enumerate(df.columns):
            ax.plot(df.index, df[col])#, styles[i], **(kwargs[i]))

        if self.xp_ware_name_map is None:
            ax.legend(self.get_data_frame().columns)
        else:
            ax.legend([self.xp_ware_name_map[x] for x in self.get_data_frame().columns])

        return ax


class BoxMPL(BoxPlot):
    """
    Creation of a static box plot.
    """

    def get_figure(self):
        """

        @return: the figure.
        """
        df = self.get_data_frame()

        fig, ax = plt.subplots()
        ax.set_title(self.get_title())
        ax.set_xlabel(self.get_x_axis_name())
        ax.set_ylabel(self.get_y_axis_name())
        ax.set_yscale('log')

        return df.boxplot(ax=ax)


class ScatterMPL(ScatterPlot):
    """
    Creation of a static scatter plot.
    """

    def get_figure(self):
        """

        @return: the figure.
        """
        df = self.get_data_frame()
        limits = [self.min, self.campaign_df.campaign.timeout]

        fig, ax = plt.subplots()
        ax.set_title(self.get_title())
        ax.set_xlabel(self.get_x_axis_name())
        ax.set_ylabel(self.get_y_axis_name())
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.plot(limits, limits, ls="--", c=".3")

        plt.xlim(limits)
        plt.ylim(limits)

        return df.plot.scatter(x=self.xp_ware_i, y=self.xp_ware_j, ax=ax)
