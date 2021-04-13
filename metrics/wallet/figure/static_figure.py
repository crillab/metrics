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

pd.set_option('display.max_rows', None)
from matplotlib import pyplot as plt

from metrics.core.constants import STAT_TABLE_COUNT, STAT_TABLE_COMMON_COUNT, STAT_TABLE_COMMON_SUM, \
    STAT_TABLE_UNCOMMON_COUNT, STAT_TABLE_TOTAL, STAT_TABLE_SUM, EXPERIMENT_XP_WARE, EXPERIMENT_CPU_TIME, \
    EXPERIMENT_INPUT
from metrics.wallet.dataframe.dataframe import CampaignDFFilter, CampaignDataFrame
from metrics.wallet.figure.abstract_figure import CactusPlot, BoxPlot, ScatterPlot, Table

LINE_STYLES = ['-', ':', '-.', '--']
"""
Corresponds to a sample of existing line styles for matplotlib.
"""

DEFAULT_COLORS = plt.rcParams['axes.prop_cycle'].by_key()['color']


class StatTable(Table):
    """
    Creation of a stat table representing main statistics for a campaign.
    """

    def __init__(self, campaign_df: CampaignDataFrame, par: List[int] = None, **kwargs):
        super().__init__(campaign_df, **kwargs)
        self._par = par or list()

    def get_data_frame(self):
        df_stat = pd.DataFrame(index=self._campaign_df.xp_ware_names)

        only_solved_df = self._campaign_df._filter_by([
            CampaignDFFilter.ONLY_SOLVED,
        ]).data_frame

        no_common_failed = self._campaign_df._filter_by([
            CampaignDFFilter.DELETE_COMMON_TIMEOUT,
        ]).data_frame.copy()

        for i in self._par:
            no_common_failed[f'PAR{i}'] = no_common_failed.apply(lambda x: x['cpu_time'] if x['success'] else self._campaign_df.campaign.timeout * i, axis=1)

        common_inputs = self._campaign_df._filter_by([
            CampaignDFFilter.ONLY_COMMON_SOLVED,
        ]).data_frame

        no_common_solved_no_out = self._campaign_df._filter_by([
            CampaignDFFilter.DELETE_COMMON_SOLVED,
            CampaignDFFilter.ONLY_SOLVED,
        ]).data_frame

        df_stat[STAT_TABLE_COUNT] = only_solved_df.groupby(EXPERIMENT_XP_WARE)[EXPERIMENT_CPU_TIME].count()
        df_stat[STAT_TABLE_SUM] = no_common_failed.groupby(EXPERIMENT_XP_WARE)[EXPERIMENT_CPU_TIME].sum()
        for i in self._par:
            df_stat[STAT_TABLE_SUM + f'PAR{i}'] = no_common_failed.groupby(EXPERIMENT_XP_WARE)[f'PAR{i}'].sum()
        df_stat[STAT_TABLE_COMMON_COUNT] = common_inputs.groupby(EXPERIMENT_XP_WARE)[EXPERIMENT_CPU_TIME].count()
        df_stat[STAT_TABLE_COMMON_SUM] = common_inputs.groupby(EXPERIMENT_XP_WARE)[EXPERIMENT_CPU_TIME].sum()
        df_stat[STAT_TABLE_UNCOMMON_COUNT] = no_common_solved_no_out.groupby(EXPERIMENT_XP_WARE)[
            EXPERIMENT_CPU_TIME].count()
        df_stat[STAT_TABLE_TOTAL] = len(self._campaign_df.data_frame[EXPERIMENT_INPUT].unique())

        return df_stat.sort_values(['count', 'sum'], ascending=[False, True]).fillna(0).astype(int)


def contribution_agg(slice: pd.DataFrame, to: float):
    slice = slice.sort_values(by=EXPERIMENT_CPU_TIME)
    first = slice.iloc[0]
    second = slice.iloc[1]

    if first[EXPERIMENT_CPU_TIME] < to:
        return pd.Series([first[EXPERIMENT_XP_WARE], first[EXPERIMENT_CPU_TIME], second[EXPERIMENT_CPU_TIME] >= to],
                         index=['first', EXPERIMENT_CPU_TIME, 'unique'])

    return pd.Series([None, None, False], index=['first', EXPERIMENT_CPU_TIME, 'unique'])


class ContributionTable(Table):
    """
    Creation of a table representing the different contributions of each solver.
    """

    def __init__(self, campaign_df: CampaignDataFrame, deltas: List[float], **kwargs):
        super().__init__(campaign_df, **kwargs)
        self._deltas = deltas

    def get_data_frame(self):
        contrib_raw = self._campaign_df.data_frame.groupby(EXPERIMENT_INPUT).apply(
            lambda x: contribution_agg(x, self._campaign_df.campaign.timeout))
        contrib = pd.DataFrame()

        contrib['vbew simple'] = contrib_raw.groupby('first').cpu_time.count()

        for delta in self._deltas:
            sub = contrib_raw[contrib_raw.cpu_time > delta]
            contrib[f'vbew {delta}s'] = sub.groupby('first').cpu_time.count()

        contrib['contribution'] = contrib_raw.groupby('first').unique.sum()

        contrib.index.name = None

        return contrib.fillna(0).astype(int).sort_values(['vbew simple', 'contribution'], ascending=[False, False])


class ErrorTable(Table):
    """
    Creation of a table representing the different contributions of each solver.
    """

    def __init__(self, campaign_df: CampaignDataFrame, **kwargs):
        super().__init__(campaign_df, **kwargs)

    def get_data_frame(self):
        df = self._campaign_df.data_frame.copy()
        df[EXPERIMENT_CPU_TIME] = df.apply(lambda x: x[EXPERIMENT_CPU_TIME] if not x['missing'] else None, axis=1)
        df = df.pivot(index=EXPERIMENT_INPUT, columns=EXPERIMENT_XP_WARE, values=EXPERIMENT_CPU_TIME)

        df['n_errors'] = df.isnull().sum(axis=1)

        return df[df.n_errors > 0]


class PivotTable(Table):
    """
    ...
    """

    def __init__(self, campaign_df: CampaignDataFrame, pivot_val, **kwargs):
        super().__init__(campaign_df, **kwargs)
        self._pivot_val = pivot_val

    def get_data_frame(self):
        df_solved = self._campaign_df.data_frame
        return df_solved.pivot(index=EXPERIMENT_INPUT, columns=EXPERIMENT_XP_WARE, values=self._pivot_val)


class Description:

    def __init__(self, campaign_df: CampaignDataFrame, show_experiment_wares=False, show_inputs=False,
                 show_variables=False):
        self._campaign_df = campaign_df
        self._show_experiment_wares = show_experiment_wares
        self._show_inputs = show_inputs
        self._show_variables = show_variables

    def get_description(self):
        df = self._campaign_df.data_frame
        missing = df['missing'].sum()
        total = len(df)

        return f"""
This analysis is composed of:
- {len(self._campaign_df.xp_ware_names)} experiment-wares{self._get_xp_wares()} 
- {len(self._campaign_df.inputs)} inputs{self._get_inputs()}
- {total - missing} experiments ({missing} missing -> more details: <Analysis>.get_error_table())
"""

    def _get_xp_wares(self):
        if not self._show_experiment_wares:
            return ''
        return ':\n' + ',\n'.join(self._campaign_df.xp_ware_names) + ',\n'

    def _get_inputs(self):
        if not self._show_inputs:
            return ''
        return ':\n' + ',\n'.join(self._campaign_df.inputs) + ',\n'


class CactusMPL(CactusPlot):
    """
    Creation of a static cactus plot.
    """

    def __init__(self, campaign_df, ax=None, **kwargs):
        super().__init__(campaign_df, **kwargs)
        self._ax = ax

    def get_figure(self):
        """

        @return: the figure.
        """
        df = self.get_data_frame()
        self._set_font()

        if self._ax is not None:
            ax = self._ax
        else:
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
            self._set_legend(df, ax)

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
                'linewidth': 1.5,
                'marker': 'o' if self._show_marker else None,
            } for x in df.columns
        ]

        for i, col in enumerate(df.columns):
            if styles is None:
                ax.plot(df.index, df[col], label=self._get_final_xpware_name(col), **(kwargs[i]))
            else:
                ax.plot(df.index, df[col], styles[i], label=self._get_final_xpware_name(col), **(kwargs[i]))

    def _set_legend(self, df, ax):
        colors = ['lightgray' if self._style_map.get(x) == ' ' else 'black' for x in
                  df.columns] if self._style_map else None

        if self._xp_ware_name_map is None:
            leg = ax.legend(self.get_data_frame().columns, loc=self._legend_location,
                            bbox_to_anchor=self._bbox_to_anchor,
                            ncol=self._ncol_legend)
        else:
            leg = ax.legend([self._get_final_xpware_name(x) for x in self.get_data_frame().columns],
                            loc=self._legend_location,
                            bbox_to_anchor=self._bbox_to_anchor, ncol=self._ncol_legend)

        if colors is not None:
            for color, text in zip(colors, leg.get_texts()):
                text.set_color(color)


class CDFMPL(CactusMPL):
    """
    Creation of a Cumulative Distribution Function to compare the performance of several solvers.
    """

    def __init__(self, campaign_df, cdf_col=EXPERIMENT_CPU_TIME, **kwargs):
        super().__init__(campaign_df, cactus_col=cdf_col, **kwargs)

    def get_figure(self):
        """

        @return: the figure.
        """
        df = self.get_data_frame()
        self._set_font()

        fig, ax = plt.subplots(figsize=self._figsize)
        ax.set_title(self.get_title())
        ax.set_xlabel(self.get_y_axis_name())
        ax.set_ylabel(self.get_x_axis_name())
        ax.set_xscale('log' if self._logx else 'linear')
        ax.set_yscale('log' if self._logy else 'linear')

        self._set_plot(df, ax)

        if self._legend_location is None:
            ax.legend().remove()
        else:
            self._set_legend(df, ax)

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
                'linewidth': 3 if x in self._campaign_df.vbew_names else 2,
                'marker': 'o' if self._show_marker else None,
            } for x in df.columns
        ]

        n_inputs = len(self._campaign_df.inputs)

        for i, col in enumerate(df.columns):
            if styles is None:
                ax.plot(df[col], df.index / n_inputs, label=self._get_final_xpware_name(col), **(kwargs[i]))
            else:
                ax.plot(df[col], df.index / n_inputs, styles[i], label=self._get_final_xpware_name(col), **(kwargs[i]))


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

    def __init__(self, campaign_df: CampaignDataFrame, xp_ware_x, xp_ware_y, **kwargs):
        super().__init__(campaign_df, xp_ware_x, xp_ware_y, **kwargs)

    def get_figure(self):
        """

        @return: the figure.
        """
        df = self.get_data_frame()
        self._set_font()
        lim_min = min(self._x_min, self._y_min) if self._x_min != -1 and self._y_min != -1 else self._min
        lim_max = max(self._x_max, self._y_max) if self._x_max != -1 and self._y_max != -1 else self._campaign_df.campaign.timeout
        limits = [lim_min, lim_max]

        fig, ax = plt.subplots(figsize=self._figsize)
        ax.set_title(self.get_title())
        ax.set_xscale('log' if self._logx else 'linear')
        ax.set_yscale('log' if self._logy else 'linear')
        ax.plot(limits, limits, ls="--", c=".3", label=None)

        plt.xlim(limits)
        plt.ylim(limits)

        ax.set_xlim(self._get_x_lim(ax))
        ax.set_ylim(self._get_y_lim(ax))

        self._extra_col(df, self._color_col)

        if self._color_col is None:
            df.plot.scatter(x=self._xp_ware_i, y=self._xp_ware_j, ax=ax)
        else:
            names = []
            for name, sub in df.groupby(self._color_col):
                ax.scatter(sub[self._xp_ware_i], sub[self._xp_ware_j], label=name.replace("'", ''))
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
        return ''