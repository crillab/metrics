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

import pandas as pd
from matplotlib import pyplot as plt

from metrics.wallet.dataframe.dataframe import CampaignDFFilter, CampaignDataFrame
from metrics.wallet.figure.abstract_figure import CactusPlot, BoxPlot, ScatterPlot, Table, CDFPlot

LINE_STYLES = ['-', ':', '-.', '--']
"""
Corresponds to a sample of existing line styles for matplotlib.
"""

DEFAULT_COLORS = plt.rcParams['axes.prop_cycle'].by_key()['color']


class StatTable(Table):
    """
    Creation of a stat table representing main statistics for a campaign.
    """

    def get_data_frame(self):
        df_stat = pd.DataFrame(index=self._campaign_df.xp_ware_names)

        only_solved_df = self._campaign_df.filter_by([
            CampaignDFFilter.ONLY_SOLVED,
        ]).data_frame

        no_common_failed = self._campaign_df.filter_by([
            CampaignDFFilter.DELETE_COMMON_TIMEOUT,
        ]).data_frame

        common_inputs = self._campaign_df.filter_by([
            CampaignDFFilter.ONLY_COMMON_SOLVED,
        ]).data_frame

        no_common_solved_no_out = self._campaign_df.filter_by([
            CampaignDFFilter.DELETE_COMMON_SOLVED,
            CampaignDFFilter.ONLY_SOLVED,
        ]).data_frame

        df_stat['count'] = only_solved_df.groupby('experiment_ware')['cpu_time'].count()
        df_stat['sum'] = no_common_failed.groupby('experiment_ware')['cpu_time'].sum()
        df_stat['common count'] = common_inputs.groupby('experiment_ware')['cpu_time'].count()
        df_stat['common sum'] = common_inputs.groupby('experiment_ware')['cpu_time'].sum()
        df_stat['uncommon count'] = no_common_solved_no_out.groupby('experiment_ware')['cpu_time'].count()
        df_stat['total'] = len(self._campaign_df.data_frame['input'].unique())

        return df_stat.sort_values(['count', 'sum'], ascending=[False, True]).fillna(0).astype(int)


def contribution_agg(slice: pd.DataFrame, to: float):
    slice = slice.sort_values(by='cpu_time')
    first = slice.iloc[0]
    second = slice.iloc[1]

    if first['cpu_time'] < to:
        return pd.Series([first['experiment_ware'], first['cpu_time'], second['cpu_time'] >= to],
                         index=['first', 'cpu_time', 'unique'])

    return pd.Series([None, None, False], index=['first', 'cpu_time', 'unique'])


class ContributionTable(Table):
    """
    Creation of a table representing the different contributions of each solver.
    """

    def __init__(self, campaign_df: CampaignDataFrame, deltas: List[float], **kwargs):
        super().__init__(campaign_df, **kwargs)
        self._deltas = deltas

    def get_data_frame(self):
        contrib_raw = self._campaign_df.data_frame.groupby('input').apply(
            lambda x: contribution_agg(x, self._campaign_df.campaign.timeout))
        contrib = pd.DataFrame()

        contrib['vbew simple'] = contrib_raw.groupby('first').cpu_time.count()

        for delta in self._deltas:
            sub = contrib_raw[contrib_raw.cpu_time > delta]
            contrib[f'vbew {delta}s'] = sub.groupby('first').cpu_time.count()

        contrib['contribution'] = contrib_raw.groupby('first').unique.sum()

        return contrib.fillna(0).astype(int).sort_values(['vbew simple', 'contribution'], ascending=[False, False])


class CactusMPL(CactusPlot):
    """
    Creation of a static cactus plot.
    """

    def get_figure(self):
        """

        @return: the figure.
        """
        df = self.get_data_frame()
        self._set_font()

        fig, ax = plt.subplots(figsize=self._figsize)
        ax.set_title(self.get_title())
        ax.set_xlabel(self.get_x_axis_name())
        ax.set_ylabel(self.get_y_axis_name())
        ax.set_xscale('log' if self._logx else 'linear')
        ax.set_yscale('log' if self._logy else 'linear')

        self._set_plot(df, ax)

        if self._legend_location is None:
            ax.legend().remove()
        else:
            self._set_legend(ax)

        ax.set_xlim(self._get_x_lim(ax))
        ax.set_ylim(self._get_y_lim(ax))

        if self._output is not None:
            fig.savefig(self._output, bbox_inches='tight', transparent=True)

        return ax

    def _set_plot(self, df, ax):
        styles = [self._style_map.get(x) for x in df.columns] if self._style_map else None

        kwargs = [
            {
                'color': self._color_map.get(x) if self._color_map else None,
                'linewidth': 3 if x in self._campaign_df.vbew_names else 1,
                'marker': 'o' if self._show_marker else None,
            } for x in df.columns
        ]

        for i, col in enumerate(df.columns):
            if styles is None:
                ax.plot(df.index, df[col], label=self._get_final_xpware_name(col), **(kwargs[i]))
            else:
                ax.plot(df.index, df[col], styles[i], label=self._get_final_xpware_name(col), **(kwargs[i]))

    def _set_legend(self, ax):
        if self._xp_ware_name_map is None:
            ax.legend(self.get_data_frame().columns, loc=self._legend_location, bbox_to_anchor=self._bbox_to_anchor,
                      ncol=self._ncol_legend)
        else:
            ax.legend([self._xp_ware_name_map[x] for x in self.get_data_frame().columns], loc=self._legend_location,
                      bbox_to_anchor=self._bbox_to_anchor, ncol=self._ncol_legend)


class CDFMPL(CDFPlot):
    """
    Creation of a static cactus plot.
    """

    def get_figure(self):
        """

        @return: the figure.
        """
        df = self.get_data_frame()
        self._set_font()

        fig, ax = plt.subplots(figsize=self._figsize)
        ax.set_title(self.get_title())
        ax.set_xlabel(self.get_x_axis_name())
        ax.set_ylabel(self.get_y_axis_name())
        ax.set_xscale('log' if self._logx else 'linear')
        ax.set_yscale('log' if self._logy else 'linear')

        self._set_plot(df, ax)
        self._set_legend(ax)

        ax.set_xlim(self._get_x_lim(ax))
        ax.set_ylim(self._get_y_lim(ax))

        if self._output is not None:
            fig.savefig(self._output, bbox_inches='tight', transparent=True)

        return ax

    def _set_plot(self, df, ax):
        styles = [self._style_map.get(x) for x in df.columns] if self._style_map else None

        kwargs = [
            {
                'color': self._color_map.get(x) if self._color_map else None,
                'linewidth': 3 if x in self._campaign_df.vbew_names else 1,
            } for x in df.columns
        ]

        for i, col in enumerate(df.columns):
            if styles is None:
                ax.hist(df[col].dropna(), int(self._campaign_df.campaign.timeout), label=self._get_final_xpware_name(col), density=True, histtype='step', cumulative=True, **(kwargs[i]))
            else:
                ax.hist(df[col].dropna(), int(self._campaign_df.campaign.timeout), label=self._get_final_xpware_name(col), density=True, histtype='step', cumulative=True, **(kwargs[i]))

    def _set_legend(self, ax):
        if self._xp_ware_name_map is None:
            ax.legend(self.get_data_frame().columns, loc=self._legend_location, bbox_to_anchor=self._bbox_to_anchor,
                      ncol=self._ncol_legend)
        else:
            ax.legend([self._xp_ware_name_map[x] for x in self.get_data_frame().columns], loc=self._legend_location,
                      bbox_to_anchor=self._bbox_to_anchor, ncol=self._ncol_legend)


class BoxMPL(BoxPlot):
    """
    Creation of a static box plot.
    """

    def get_figure(self):
        """

        @return: the figure.
        """
        df = self.get_data_frame()
        self._set_font()

        fig, ax = plt.subplots(figsize=self._figsize)
        ax.set_title(self.get_title())
        ax.set_xlabel(self.get_x_axis_name())
        ax.set_xscale('log' if self._logx else 'linear')

        if self._xp_ware_name_map is not None:
            df = df.rename(columns=self._xp_ware_name_map)

        df.boxplot(ax=ax, rot=0, meanline=True, showmeans=True, vert=False, grid=False)

        if self._output is not None:
            fig.savefig(self._output, bbox_inches='tight', transparent=True)

        return ax


class ScatterMPL(ScatterPlot):
    """
    Creation of a static scatter plot.
    """

    def __init__(self, campaign_df: CampaignDataFrame, xp_ware_x, xp_ware_y, color_col=None, **kwargs):
        super().__init__(campaign_df, xp_ware_x, xp_ware_y, **kwargs)
        self._color_col = color_col

    def get_figure(self):
        """

        @return: the figure.
        """
        df = self.get_data_frame()
        self._set_font()
        limits = [self._min, self._campaign_df.campaign.timeout]

        fig, ax = plt.subplots(figsize=self._figsize)
        ax.set_title(self.get_title())
        ax.set_xscale('log' if self._logx else 'linear')
        ax.set_yscale('log' if self._logy else 'linear')
        ax.plot(limits, limits, ls="--", c=".3")

        plt.xlim(limits)
        plt.ylim(limits)

        ax.set_xlim(self._get_x_lim(ax))
        ax.set_ylim(self._get_y_lim(ax))

        self._extra_col(df, self._color_col)

        if self._color_col is None:
            df.plot.scatter(x=self._xp_ware_i, y=self._xp_ware_j, ax=ax)
        else:
            for name, sub in df.groupby(self._color_col):
                ax.scatter(sub[self._xp_ware_i], sub[self._xp_ware_j], label=name)
            plt.legend(title=None)

        ax.set_xlabel(self.get_x_axis_name())
        ax.set_ylabel(self.get_y_axis_name())

        if self._output is not None:
            fig.savefig(self._output, bbox_inches='tight', transparent=True)

        return ax

    def get_x_axis_name(self):
        """

        @return: the x axis name.
        """
        return self._get_final_xpware_name(self._xp_ware_i)

    def get_y_axis_name(self):
        """

        @return: the y axis name.
        """
        return self._get_final_xpware_name(self._xp_ware_j)

    def get_title(self):
        """

        @return: the title of the plot.
        """
        return f'Comparison of {self._get_final_xpware_name(self._xp_ware_i)} and {self._get_final_xpware_name(self._xp_ware_j)}'

    def _extra_col(self, df, col):
        if col is None:
            return

        ori = self._campaign_df.data_frame
        df[col] = ori.groupby('input')['sat'].agg(lambda x: str(set(x) - {None}))
