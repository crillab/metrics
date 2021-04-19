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

import pickle
from typing import Callable, Any, List
import warnings

import numpy as np
from autograph import create_plot
from autograph.core.enumstyle import Position, FontWeight, LineType
from autograph.core.style import LegendStyle, TextStyle, PlotStyle

warnings.formatwarning = lambda msg, *args, **kwargs: str(msg) + '\n'

from pandas import DataFrame
from itertools import product
import pandas as pd

from metrics.core.model import Campaign
from metrics.core.constants import *
from metrics.scalpel import read_campaign


def find_best_cpu_time_input(df):
    df2 = df[df[SUCCESS_COL]]

    if len(df2) > 0:
        s = df2[EXPERIMENT_CPU_TIME]
        return df2[s == s.min()]

    s = df[EXPERIMENT_CPU_TIME]
    return df[s == s.min()]


def export_data_frame(data_frame, output=None, commas_for_number=False, dollars_for_number=False,
                      **kwargs):
    if output is None:
        return data_frame

    df = data_frame

    if commas_for_number:
        df = df.applymap(lambda x: f"{x:,}")

    if dollars_for_number:
        df = df.applymap(lambda x: f"${x}$")

    ext = output.split('.')[-1]

    if ext == 'tex':
        with open(output, 'w') as file:
            df.to_latex(
                buf=file,
                escape=False,
                index_names=False,
                bold_rows=True,
                **kwargs
            )
    else:
        raise ValueError('Only .tex extension is accepted.')

    return data_frame


def _cpu_time_stat(x, i):
    return x[EXPERIMENT_CPU_TIME] if x[SUCCESS_COL] else x[TIMEOUT_COL] * i


def _compute_cpu_time_stats(df, par):
    return pd.Series({**{
        STAT_TABLE_COUNT: df[SUCCESS_COL].sum(),
        STAT_TABLE_SUM: df.apply(lambda x: _cpu_time_stat(x, 1), axis=1).sum(),
    }, **{
        STAT_TABLE_PAR + str(i): df.apply(lambda x: _cpu_time_stat(x, i), axis=1).sum() for i in par
    }})


def _contribution_agg(sli: pd.DataFrame):
    sli = sli.sort_values(by=EXPERIMENT_CPU_TIME)
    first = sli.iloc[0]
    second = sli.iloc[1]
    index = [EXPERIMENT_XP_WARE, EXPERIMENT_CPU_TIME, 'unique']

    if first[EXPERIMENT_CPU_TIME] < first[TIMEOUT_COL]:
        return pd.Series(
            [first[EXPERIMENT_XP_WARE], first[EXPERIMENT_CPU_TIME],
             second[EXPERIMENT_CPU_TIME] >= second[TIMEOUT_COL]],
            index=index)

    return pd.Series([None, None, False], index=index)


def _make_cactus_plot_df(analysis, cumulated, cactus_col):
    df_solved = analysis.data_frame[analysis.data_frame[SUCCESS_COL]]
    df_cactus = df_solved.pivot(columns=EXPERIMENT_XP_WARE, values=cactus_col)
    for col in df_cactus.columns:
        df_cactus[col] = df_cactus[col].sort_values().values
    df_cactus = df_cactus.dropna(how='all').reset_index(drop=True)
    df_cactus.index += 1
    # df_cactus = df_cactus[df_cactus.index > self._x_min]

    order = (df_cactus.count() - (df_cactus.sum() / 10 ** 10)).sort_values(ascending=False).index
    df_cactus = df_cactus[order]

    return df_cactus.cumsum() if cumulated else df_cactus


def _make_cdf_plot_df(analysis, cumulated, cdf_col):
    df = _make_cactus_plot_df(analysis, cumulated, cdf_col)
    return df.T


def _make_scatter_plot_df(analysis, xp_ware_x, xp_ware_y, scatter_col, color_col=None):
    df = analysis.keep_experiment_wares({xp_ware_x, xp_ware_y}).data_frame
    index = [EXPERIMENT_INPUT]
    if color_col is not None:
        index.append(color_col)
    return df[df[SUCCESS_COL]].pivot_table(
        index=index,
        columns=EXPERIMENT_XP_WARE,
        values=scatter_col,
        fill_value=analysis.data_frame[TIMEOUT_COL].max()
    )


def _make_box_plot_df(analysis, box_col):
    return analysis.data_frame.pivot(columns=EXPERIMENT_XP_WARE, values=box_col)


class Analysis:

    def __init__(self, input_file: str = None, data_frame: DataFrame = None,
                 is_consistent_by_xp: Callable[[Any], bool] = None,
                 is_consistent_by_input: Callable[[Any], bool] = None,
                 is_success: Callable[[Any], bool] = None):

        if data_frame is not None:
            self._data_frame = data_frame
            is_succ = is_success
            inputs = self.inputs
            experiment_wares = self.experiment_wares

        else:
            campaign, config = read_campaign(input_file)

            self._data_frame = DataFrameBuilder(campaign).build_from_campaign()
            self._data_frame[TIMEOUT_COL] = campaign.timeout
            self._data_frame[ERROR_COL] = False

            is_succ = config.get_is_success() if is_success is None else is_success
            inputs = campaign.get_input_set().get_input_names()
            experiment_wares = campaign.get_experiment_ware_names()

        self.check_success(is_succ)
        self.check_missing_experiments(inputs, experiment_wares)
        self.check_xp_consistency(is_consistent_by_xp)
        self.check_input_consistency(is_consistent_by_input)

    @property
    def data_frame(self):
        return self._data_frame

    @property
    def inputs(self) -> List[str]:
        """

        @return: the input names of the dataframe.
        """
        return self._data_frame[EXPERIMENT_INPUT].unique()

    @property
    def experiment_wares(self) -> List[str]:
        """

        @return: the experimentware names of the dataframe.
        """
        return self._data_frame[EXPERIMENT_XP_WARE].unique()

    def _update_error_and_success_cols(self, new_error_series):
        self._data_frame[ERROR_COL] = (self._data_frame[ERROR_COL]) | new_error_series
        self._data_frame[SUCCESS_COL] = (self._data_frame[SUCCESS_COL]) & (
            ~self._data_frame[ERROR_COL])

    def check_success(self, is_success: Callable[[Any], bool]):
        if is_success is None:
            return
        self._data_frame[SUCCESS_COL] = self._data_frame.apply(is_success, axis=1)

    def check_missing_experiments(self, inputs: List[str], experiment_wares: List[str]):
        theoretical_df = DataFrame(product(inputs, experiment_wares),
                                   columns=[EXPERIMENT_INPUT, EXPERIMENT_XP_WARE])

        self._data_frame[MISSING_DATA_COL] = False
        self._data_frame = self._data_frame.join(
            theoretical_df.set_index([EXPERIMENT_INPUT, EXPERIMENT_XP_WARE]), how='right',
            on=[EXPERIMENT_INPUT, EXPERIMENT_XP_WARE])
        self._data_frame[MISSING_DATA_COL] = self._data_frame[MISSING_DATA_COL].fillna(True)

        self._update_error_and_success_cols(self._data_frame[MISSING_DATA_COL])

        n_missing = self._data_frame[MISSING_DATA_COL].sum()

        if n_missing > 0:
            warnings.warn(
                f'{n_missing} experiments are missing and have been added as unsuccessful.')

    def check_xp_consistency(self, is_consistent: Callable[[Any], bool]):
        if is_consistent is None:
            return

        self._data_frame[XP_CONSISTENCY_COL] = self._data_frame.apply(is_consistent, axis=1)

        inconsistency = ~self._data_frame[XP_CONSISTENCY_COL]

        self._update_error_and_success_cols(inconsistency)

        n_inconsistencies = inconsistency.sum()

        if n_inconsistencies > 0:
            warnings.warn(
                f'{n_inconsistencies} experiments are inconsistent and are declared as unsuccessful.')

    def check_input_consistency(self, is_consistent: Callable[[Any], bool]):
        if is_consistent is None:
            return

        s = self._data_frame.groupby(EXPERIMENT_INPUT).apply(is_consistent)

        inconsistent_inputs = set(s[~s].index)

        self._data_frame[INPUT_CONSISTENCY_COL] = ~self._data_frame[EXPERIMENT_INPUT].isin(
            inconsistent_inputs)
        self._update_error_and_success_cols(~self._data_frame[INPUT_CONSISTENCY_COL])

        if len(inconsistent_inputs) > 0:
            warnings.warn(
                f'{len(inconsistent_inputs)} inputs are inconsistent and linked experiments are now declared as unsuccessful.')

    def add_variable(self, new_var, function, inplace=False):
        df = self._data_frame if inplace else self._data_frame.copy()
        df[new_var] = df.apply(function, axis=1)
        return self if inplace else self.__class__(data_frame=df)

    def remove_variables(self, vars: List[str], inplace=False):
        df = self._data_frame.drop(columns=vars, inplace=inplace)
        return self if inplace else self.__class__(data_frame=df)

    def add_analysis(self, analysis,
                     is_consistent_by_xp: Callable[[Any], bool] = None,
                     is_consistent_by_input: Callable[[Any], bool] = None,
                     is_success: Callable[[Any], bool] = None):
        return self.add_data_frame(analysis.data_frame, is_consistent_by_xp, is_consistent_by_input,
                                   is_success)

    def add_data_frame(self, data_frame,
                       is_consistent_by_xp: Callable[[Any], bool] = None,
                       is_consistent_by_input: Callable[[Any], bool] = None,
                       is_success: Callable[[Any], bool] = None):
        return self.__class__(
            data_frame=self._data_frame.append(data_frame, ignore_index=True).copy(),
            is_consistent_by_xp=is_consistent_by_xp,
            is_consistent_by_input=is_consistent_by_input,
            is_success=is_success
        )

    def add_virtual_experiment_ware(self, function=find_best_cpu_time_input, xp_ware_set=None,
                                    name='vbew') -> Analysis:
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
        df = self._data_frame
        if xp_ware_set is None:
            xp_ware_set = self.experiment_wares

        df_vbs = df[df[EXPERIMENT_XP_WARE].isin(xp_ware_set)]

        df_vbs = df_vbs.groupby(EXPERIMENT_INPUT).apply(function).dropna(how='all') \
            .assign(experiment_ware=lambda x: name)

        return self.add_data_frame(data_frame=df_vbs.copy())

    def filter_analysis(self, function) -> Analysis:
        """
        Filters the dataframe in function of sub set of authorized values for a given column.
        @param column: column where  to keep the sub set of values.
        @param sub_set: the sub set of authorised values.
        @return: the filtered dataframe in a new instance of Analysis.
        """
        return self.__class__(
            data_frame=self._data_frame[self._data_frame.apply(function, axis=1)].copy())

    def remove_experiment_wares(self, experiment_wares) -> Analysis:
        """
        Filters the dataframe in function of sub set of authorized values for a given column.
        @param column: column where  to keep the sub set of values.
        @param sub_set: the sub set of authorised values.
        @return: the filtered dataframe in a new instance of Analysis.
        """
        return self.filter_analysis(lambda x: x[EXPERIMENT_XP_WARE] not in experiment_wares)

    def keep_experiment_wares(self, experiment_wares) -> Analysis:
        """
        Filters the dataframe in function of sub set of authorized values for a given column.
        @param column: column where  to keep the sub set of values.
        @param sub_set: the sub set of authorised values.
        @return: the filtered dataframe in a new instance of Analysis.
        """
        return self.filter_analysis(lambda x: x[EXPERIMENT_XP_WARE] in experiment_wares)

    def filter_inputs(self, function, how='all') -> Analysis:
        """
        Filters the dataframe in function of sub set of authorized values for a given column.
        @param column: column where  to keep the sub set of values.
        @param sub_set: the sub set of authorised values.
        @return: the filtered dataframe in a new instance of Analysis.
        """
        if how == 'all':
            s = self._data_frame.groupby(EXPERIMENT_INPUT).apply(
                lambda df: df.apply(function, axis=1).all())
        elif how == 'any':
            s = self._data_frame.groupby(EXPERIMENT_INPUT).apply(
                lambda df: df.apply(function, axis=1).any())
        else:
            raise AttributeError(
                '"how" parameter could only takes these next values: "all" or "any".')

        return self.__class__(
            data_frame=self._data_frame[self._data_frame[EXPERIMENT_INPUT].isin(s[s].index)].copy())

    def delete_common_failed_inputs(self):
        return self.filter_inputs(
            function=lambda x: x[SUCCESS_COL],
            how='any'
        )

    def delete_common_solved_inputs(self):
        return self.filter_inputs(
            function=lambda x: not x[SUCCESS_COL],
            how='any'
        )

    def keep_common_failed_inputs(self):
        return self.filter_inputs(
            function=lambda x: not x[SUCCESS_COL],
            how='all'
        )

    def keep_common_solved_inputs(self):
        return self.filter_inputs(
            function=lambda x: x[SUCCESS_COL],
            how='all'
        )

    def all_experiment_ware_pair_analysis(self) -> List[Analysis]:
        xpw = self.experiment_wares

        return [
            self.keep_experiment_wares([xpw[i], j]) for i in range(len(xpw) - 1) for j in
            xpw[i + 1:]
        ]

    def groupby(self, column) -> List[Analysis]:
        """
        Makes a group by a given column.
        @param column: column where to applu the groupby.
        @return: a list of Analysis with each group.
        """
        return [
            self.__class__(data_frame=group.copy()) for _, group in self._data_frame.groupby(column)
        ]

    def error_table(self, **kwargs):
        return export_data_frame(
            data_frame=self._data_frame[self._data_frame.error].copy(),
            **kwargs
        )

    def description_table(self, **kwargs):
        df = self._data_frame

        return export_data_frame(
            data_frame=pd.Series({
                'n_experiment_wares': len(self.experiment_wares),
                'n_inputs': len(self.inputs),
                'n_experiments': len(df),
                'n_missing_xp': (df['missing']).sum(),
                'n_inconsistent_xp': (~df['consistent_xp']).sum(),
                'n_inconsistent_xp_due_to_input': (~df['consistent_input']).sum(),
                'more_info_about_variables': "<analysis>.data_frame.describe(include='all')"
            }, name='analysis').to_frame(),
            **kwargs
        )

    def pivot_table(self, index=EXPERIMENT_INPUT, columns=EXPERIMENT_XP_WARE,
                    values=EXPERIMENT_CPU_TIME, **kwargs):
        return export_data_frame(
            data_frame=self._data_frame.pivot(
                index=index,
                columns=columns,
                values=values
            ),
            **kwargs
        )

    def stat_table(self, par=[1, 2, 10], **kwargs):
        stats = self._data_frame.groupby(EXPERIMENT_XP_WARE).apply(
            lambda df: _compute_cpu_time_stats(df, par))
        common = self.keep_common_solved_inputs().data_frame
        stats[STAT_TABLE_COMMON_COUNT] = common.groupby(EXPERIMENT_XP_WARE).apply(
            lambda df: df[SUCCESS_COL].sum())
        stats[STAT_TABLE_COMMON_SUM] = common.groupby(EXPERIMENT_XP_WARE).apply(
            lambda df: df.apply(lambda x: _cpu_time_stat(x, 1), axis=1).sum())
        stats[STAT_TABLE_UNCOMMON_COUNT] = stats[STAT_TABLE_COUNT] - stats[STAT_TABLE_COMMON_COUNT]
        stats[STAT_TABLE_TOTAL] = len(self.inputs)

        return export_data_frame(
            data_frame=stats.sort_values([STAT_TABLE_COUNT, STAT_TABLE_SUM],
                                         ascending=[False, True]).astype(int),
            **kwargs
        )

    def contribution_table(self, deltas=[1, 10, 100], **kwargs):
        contrib_raw = self._data_frame.groupby(EXPERIMENT_INPUT).apply(
            lambda x: _contribution_agg(x))
        contrib = pd.DataFrame()

        contrib['vbew simple'] = contrib_raw.groupby(EXPERIMENT_XP_WARE).cpu_time.count()

        for delta in deltas:
            sub = contrib_raw[contrib_raw.cpu_time > delta]
            contrib[f'vbew {delta}s'] = sub.groupby(EXPERIMENT_XP_WARE).cpu_time.count()

        contrib['contribution'] = contrib_raw.groupby(EXPERIMENT_XP_WARE).unique.sum()

        return export_data_frame(
            data_frame=contrib.fillna(0).astype(int).sort_values(['vbew simple', 'contribution'],
                                                                 ascending=[False, False]),
            **kwargs
        )

    def cactus_plot(
            self,
            cumulated=False,
            cactus_col=EXPERIMENT_CPU_TIME,
            title='Cactus-plot',
            figsize=(7, 5),
            show_marker=True,
            color_map=None,
            style_map=None,
            logx: bool = False,
            logy: bool = False,
            x_axis_name='Number of solved inputs',
            y_axis_name='Time',
            x_min: float = None,
            y_min: float = None,
            x_max: float = None,
            y_max: float = None,
            title_font_name='DejaVu Sans',
            title_font_size=12,
            title_font_color='#000000',
            title_font_weight=FontWeight.BOLD,
            label_font_name='DejaVu Sans',
            label_font_size=12,
            label_font_color='#000000',
            label_font_weight=FontWeight.NORMAL,
            latex_writing: bool = False,
            output=None,
            legend_location=Position.RIGHT,
            ncol_legend=1,
            dynamic: bool = False,
            **kwargs: dict
    ):
        df = _make_cactus_plot_df(self, cumulated, cactus_col)

        plot = self.__create_plot(dynamic, label_font_color, label_font_name, label_font_size,
                                  label_font_weight, logx, logy,
                                  title, title_font_color, title_font_name, title_font_size,
                                  title_font_weight, x_axis_name, y_axis_name, figsize
                                  )
        for name, series in df.iteritems():
            plot.plot(x=series.index, y=series, label=name)

        plot.legend = LegendStyle()
        plot.legend.position = legend_location
        plot.legend.n_col = ncol_legend

        plot.x_lim = (x_min, x_max)
        plot.y_lim = (y_min, y_max)
        self.__save_plot(output, plot)

        return plot.show()

    def __create_plot(self, dynamic, label_font_color, label_font_name, label_font_size,
                      label_font_weight, logx, logy, title,
                      title_font_color, title_font_name, title_font_size, title_font_weight,
                      x_axis_name, y_axis_name, figure_size):
        plot = create_plot('plotly' if dynamic else 'matplotlib')

        plot.title = title
        plot.title_style = TextStyle()
        plot.title_style.font_name = title_font_name
        plot.title_style.size = title_font_size
        plot.title_style.weight = title_font_weight
        plot.title_style.color = title_font_color
        plot.y_label_style = TextStyle()
        plot.y_label_style.font_name = label_font_name
        plot.y_label_style.size = label_font_size
        plot.y_label_style.weight = label_font_weight
        plot.y_label_style.color = label_font_color
        plot.y_label_style = plot.y_label_style
        plot.log_x = logx
        plot.log_y = logy
        plot.x_label = x_axis_name
        plot.y_label = y_axis_name
        plot.figure_size = figure_size
        return plot

    def cdf_plot(
            self,
            cumulated=False,
            cdf_col=EXPERIMENT_CPU_TIME,
            title='Cactus-plot',
            figsize=(7, 5),
            show_marker=True,
            color_map=None,
            style_map=None,
            logx: bool = False,
            logy: bool = False,
            x_axis_name='Number of solved inputs',
            y_axis_name='Time',
            x_min: float = None,
            y_min: float = None,
            x_max: float = None,
            y_max: float = None,
            title_font_name='DejaVu Sans',
            title_font_size=12,
            title_font_color='#000000',
            title_font_weight=FontWeight.BOLD,
            label_font_name='DejaVu Sans',
            label_font_size=12,
            label_font_color='#000000',
            label_font_weight=FontWeight.NORMAL,
            latex_writing: bool = False,
            legend_location=Position.RIGHT,
            ncol_legend=1,
            output=None,
            dynamic: bool = False,
            **kwargs: dict
    ):
        df = _make_cactus_plot_df(self, cumulated, cdf_col)

        plot = self.__create_plot(dynamic, label_font_color, label_font_name, label_font_size,
                                  label_font_weight, logx, logy,
                                  title, title_font_color, title_font_name, title_font_size,
                                  title_font_weight, x_axis_name, y_axis_name, figsize
                                  )

        for name, series in df.iteritems():
            plot.plot(x=series, y=series.index / len(self.inputs), label=name)

        plot.legend = LegendStyle()
        plot.legend.position = legend_location
        plot.legend.n_col = ncol_legend

        plot.x_lim = (x_min, x_max)
        plot.y_lim = (y_min, y_max)
        self.__save_plot(output, plot)
        return plot.show()

    def scatter_plot(
            self,
            xp_ware_x,
            xp_ware_y,
            scatter_col=EXPERIMENT_CPU_TIME,
            title='Cactus-plot',
            figsize=(7, 5),
            color_col=None,
            logx: bool = False,
            logy: bool = False,
            x_min: float = None,
            y_min: float = None,
            x_max: float = None,
            y_max: float = None,
            title_font_name='DejaVu Sans',
            title_font_size=12,
            title_font_color='#000000',
            title_font_weight=FontWeight.BOLD,
            label_font_name='DejaVu Sans',
            label_font_size=12,
            label_font_color='#000000',
            label_font_weight=FontWeight.NORMAL,
            output=None,
            legend_location=Position.RIGHT,
            ncol_legend=1,
            latex_writing: bool = False,
            dynamic: bool = False,
    ):
        df = _make_scatter_plot_df(self, xp_ware_x, xp_ware_y, scatter_col, color_col)
        plot = self.__create_plot(dynamic, label_font_color, label_font_name, label_font_size,
                                  label_font_weight, logx, logy,
                                  title, title_font_color, title_font_name, title_font_size,
                                  title_font_weight, xp_ware_x, xp_ware_y, figsize)

        lim_min = min(x_min,
                      y_min) if x_min is not None and y_min is not None else 0
        lim_max = max(x_max,
                      y_max) if x_max is not None and y_max is not None else self.data_frame[
            TIMEOUT_COL].max()
        limits = [lim_min, lim_max]
        plt_style = PlotStyle()
        plt_style.line_type = LineType.DASH
        plot.plot(limits, limits, label=None, style=plt_style)
        if color_col is None:
            plot.scatter(df[xp_ware_x], df[xp_ware_y])
        else:
            for name, sub in df.groupby(color_col):
                plot.scatter(sub[xp_ware_x], sub[xp_ware_y], label=name.replace("'", ''))

        plot.legend = LegendStyle()
        plot.legend.position = legend_location
        plot.legend.n_col = ncol_legend

        plot.x_lim = (x_min, x_max)
        plot.y_lim = (y_min, y_max)
        self.__save_plot(output, plot)
        return plot.show()

    def __save_plot(self, output, plot):
        if output is not None:
            plot.save(output, bbox_inches='tight', transparent=True)

    def box_plot(self, box_col=EXPERIMENT_CPU_TIME, dynamic: bool = False, output=None, log=False,
                 title=None,title_font_size=12,
            title_font_color='#000000',
            title_font_weight=FontWeight.BOLD,):
        df = _make_box_plot_df(self, box_col)
        plot = create_plot("plotly") if dynamic else create_plot("matplotlib")
        plot.log_x = log
        plot.title = title

        plot.title_style = TextStyle()
        plot.title_style.size = title_font_size
        plot.title_style.weight = title_font_weight
        plot.title_style.color = title_font_color

        l = []
        for col in df.columns:
            l.append(df[col].dropna())
        plot.boxplot(l, labels=df.columns)
        self.__save_plot(output, plot)
        return plot.show()

    def export(self, filename=None):
        if filename is None:
            return pickle.dumps(self, protocol=pickle.HIGHEST_PROTOCOL)

        if filename.split('.')[-1] == 'csv':
            with open(filename, 'w') as file:
                return self._data_frame.to_csv(filename, index=False)
        else:
            with open(filename, 'wb') as file:
                return pickle.dump(self, file, protocol=pickle.HIGHEST_PROTOCOL)


class DataFrameBuilder:
    """
    This builder permits to make a dataframe composed of the Campaign information.
    """

    def __init__(self, campaign: Campaign):
        """
        Creates a campaign dataframe.
        @param campaign: the campaign to build as a campaign
        """
        self._campaign = campaign

    def build_from_campaign(self) -> DataFrame:
        """
        Builds a campaign dataframe directly from the original campaign.
        @return: the builded campaign dataframe.
        """
        experiment_wares_df = self._make_experiment_wares_df()
        inputs_df = self._make_inputs_df()
        experiments_df = self._make_experiments_df()

        return experiments_df \
            .join(inputs_df.set_index(INPUT_NAME), on=EXPERIMENT_INPUT, lsuffix=SUFFIX_EXPERIMENT,
                  rsuffix=SUFFIX_INPUT,
                  how='inner') \
            .join(experiment_wares_df.set_index(XP_WARE_NAME),
                  on=EXPERIMENT_XP_WARE, lsuffix=SUFFIX_EXPERIMENT, rsuffix=SUFFIX_XP_WARE,
                  how='inner'
                  )

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
