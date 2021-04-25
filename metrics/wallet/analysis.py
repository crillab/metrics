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

from metrics.wallet.plot import CactusPlot, CDFPlot, ScatterPlot, BoxPlot

warnings.formatwarning = lambda msg, *args, **kwargs: str(msg) + '\n'

from pandas import DataFrame
from itertools import product
import pandas as pd

from metrics.core.model import Campaign
from metrics.core.constants import *
from metrics.scalpel import read_campaign


def find_best_cpu_time_input(df):
    return df.sort_values(by=[SUCCESS_COL, EXPERIMENT_CPU_TIME], ascending=[False, True]).iloc[0]


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


def _make_scatter_plot_df(analysis, xp_ware_x, xp_ware_y, scatter_col, color_col=None):
    df = analysis.keep_experiment_wares({xp_ware_x, xp_ware_y}).data_frame
    df = df[df[SUCCESS_COL]]

    df1 = df.pivot_table(
        index=EXPERIMENT_INPUT,
        columns=EXPERIMENT_XP_WARE,
        values=scatter_col,
        fill_value=analysis.data_frame[TIMEOUT_COL].max()
    )

    if color_col is not None:
        df2 = df.groupby(EXPERIMENT_INPUT).apply(lambda dff: set(dff[color_col]))
        df1[color_col] = df2.apply(lambda x: list(x)[0] if len(x) == 1 else x)

    return df1


def _make_box_plot_df(analysis, box_col):
    return analysis.data_frame.pivot(
        columns=EXPERIMENT_XP_WARE,
        index=EXPERIMENT_INPUT,
        values=box_col
    )


class Analysis:

    def __init__(self, input_file: str = None, data_frame: DataFrame = None):
        if data_frame is not None:
            self._data_frame = data_frame
            self.check()
            return

        campaign, config = read_campaign(input_file)

        self._data_frame = DataFrameBuilder(campaign).build_from_campaign()
        self._data_frame[TIMEOUT_COL] = campaign.timeout
        self._data_frame[SUCCESS_COL] = True
        self._data_frame[USER_SUCCESS_COL] = True
        self._data_frame[MISSING_DATA_COL] = False
        self._data_frame[XP_CONSISTENCY_COL] = True
        self._data_frame[INPUT_CONSISTENCY_COL] = True

        self.check(
            is_success=config.get_is_success(),
            inputs=campaign.get_input_set().get_input_names(),
            experiment_wares=campaign.get_experiment_ware_names()
        )

    @property
    def data_frame(self):
        return self._data_frame

    @property
    def inputs(self) -> List[str]:
        """

        @return: the input names of the dataframe.
        """
        return list(self._data_frame[EXPERIMENT_INPUT].unique())

    @property
    def experiment_wares(self) -> List[str]:
        """

        @return: the experimentware names of the dataframe.
        """
        return list(self._data_frame[EXPERIMENT_XP_WARE].unique())

    def copy(self):
        return self.__class__(data_frame=self._data_frame.copy())

    def check(self, is_success=None, is_consistent_by_xp=None, is_consistent_by_input=None, inputs=None, experiment_wares=None):
        self.check_success(is_success)
        self.check_missing_experiments(inputs, experiment_wares)
        self.check_xp_consistency(is_consistent_by_xp)
        self.check_input_consistency(is_consistent_by_input)

    def _check_global_success(self):
        self._data_frame[SUCCESS_COL] = self._data_frame.apply(
            lambda x: x[USER_SUCCESS_COL] and not(x[MISSING_DATA_COL]) and x[XP_CONSISTENCY_COL] and x[INPUT_CONSISTENCY_COL],
            axis=1
        )

        self._data_frame[ERROR_COL] = self._data_frame.apply(
            lambda x: x[MISSING_DATA_COL] or not(x[XP_CONSISTENCY_COL]) or not(x[INPUT_CONSISTENCY_COL]),
            axis=1
        )

    def check_success(self, is_success):
        if is_success is None:
            return
        self._data_frame[USER_SUCCESS_COL] = self._data_frame.apply(is_success, axis=1)
        self._check_global_success()

    def check_missing_experiments(self, inputs: List[str]=None, experiment_wares: List[str]=None):
        inputs = self.inputs if inputs is None else inputs
        experiment_wares = self.experiment_wares if experiment_wares is None else experiment_wares

        theoretical_df = DataFrame(product(inputs, experiment_wares), columns=[EXPERIMENT_INPUT, EXPERIMENT_XP_WARE])

        self._data_frame[MISSING_DATA_COL] = False
        self._data_frame = self._data_frame.join(
            theoretical_df.set_index([EXPERIMENT_INPUT, EXPERIMENT_XP_WARE]), how='right',
            on=[EXPERIMENT_INPUT, EXPERIMENT_XP_WARE])
        self._data_frame[MISSING_DATA_COL] = self._data_frame[MISSING_DATA_COL].fillna(True)

        n_missing = self._data_frame[MISSING_DATA_COL].sum()

        if n_missing > 0:
            self._check_global_success()
            warnings.warn(
                f'{n_missing} experiments are missing and have been added as unsuccessful.')

    def check_xp_consistency(self, is_consistent):
        if is_consistent is None:
            return

        self._data_frame[XP_CONSISTENCY_COL] = self._data_frame.apply(is_consistent, axis=1)

        inconsistency = ~self._data_frame[XP_CONSISTENCY_COL]

        n_inconsistencies = inconsistency.sum()

        if n_inconsistencies > 0:
            self._check_global_success()
            warnings.warn(
                f'{n_inconsistencies} experiments are inconsistent and are declared as unsuccessful.')

    def check_input_consistency(self, is_consistent):
        if is_consistent is None:
            return

        s = self._data_frame.groupby(EXPERIMENT_INPUT).apply(is_consistent)

        inconsistent_inputs = set(s[~s].index)

        self._data_frame[INPUT_CONSISTENCY_COL] = ~self._data_frame[EXPERIMENT_INPUT].isin(
            inconsistent_inputs)

        if len(inconsistent_inputs) > 0:
            self._check_global_success()
            warnings.warn(
                f'{len(inconsistent_inputs)} inputs are inconsistent and linked experiments are now declared as unsuccessful.')

    def add_variable(self, new_var, function, inplace=False):
        if not inplace:
            return self.copy().add_variable(new_var, function, inplace=True)
        df = self._data_frame
        df[new_var] = df.apply(function, axis=1)
        return self

    def remove_variables(self, vars: List[str], inplace=False):
        if not inplace:
            return self.copy().remove_variables(vars, inplace=True)
        self._data_frame.drop(columns=vars, inplace=True)
        return self

    def add_analysis(self, analysis):
        return self.add_data_frame(analysis.data_frame)

    def add_data_frame(self, data_frame):
        return self.__class__(data_frame=self._data_frame.append(data_frame, ignore_index=True))

    def add_virtual_experiment_ware(self, function=find_best_cpu_time_input, xp_ware_set=None, name='vbew') -> Analysis:
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

        return self.add_data_frame(data_frame=df_vbs)

    def filter_analysis(self, function, inplace=False) -> Analysis:
        """
        Filters the dataframe in function of sub set of authorized values for a given column.
        @param column: column where  to keep the sub set of values.
        @param sub_set: the sub set of authorised values.
        @return: the filtered dataframe in a new instance of Analysis.
        """
        if not inplace:
            return self.copy().filter_analysis(function, inplace=True)

        self._data_frame = self._data_frame[self._data_frame.apply(function, axis=1)]

        return self

    def remove_experiment_wares(self, experiment_wares, inplace=False) -> Analysis:
        """
        Filters the dataframe in function of sub set of authorized values for a given column.
        @param column: column where  to keep the sub set of values.
        @param sub_set: the sub set of authorised values.
        @return: the filtered dataframe in a new instance of Analysis.
        """
        if not inplace:
            return self.copy().remove_experiment_wares(experiment_wares, inplace=True)

        return self.filter_analysis(lambda x: x[EXPERIMENT_XP_WARE] not in experiment_wares, inplace)

    def keep_experiment_wares(self, experiment_wares, inplace=False) -> Analysis:
        """
        Filters the dataframe in function of sub set of authorized values for a given column.
        @param column: column where  to keep the sub set of values.
        @param sub_set: the sub set of authorised values.
        @return: the filtered dataframe in a new instance of Analysis.
        """
        return self.filter_analysis(lambda x: x[EXPERIMENT_XP_WARE] in experiment_wares, inplace)

    def filter_inputs(self, function, how='all', inplace=False) -> Analysis:
        """
        Filters the dataframe in function of sub set of authorized values for a given column.
        @param column: column where  to keep the sub set of values.
        @param sub_set: the sub set of authorised values.
        @return: the filtered dataframe in a new instance of Analysis.
        """
        if not inplace:
            return self.copy().filter_inputs(function, how, inplace=True)

        if how == 'all':
            s = self._data_frame.groupby(EXPERIMENT_INPUT).apply(
                lambda df: df.apply(function, axis=1).all())
        elif how == 'any':
            s = self._data_frame.groupby(EXPERIMENT_INPUT).apply(
                lambda df: df.apply(function, axis=1).any())
        else:
            raise AttributeError(
                '"how" parameter could only takes these next values: "all" or "any".')

        self._data_frame = self._data_frame[self._data_frame[EXPERIMENT_INPUT].isin(s[s].index)]

        return self

    def delete_common_failed_inputs(self, inplace=False):
        return self.filter_inputs(
            function=lambda x: x[SUCCESS_COL],
            how='any',
            inplace=inplace
        )

    def delete_common_solved_inputs(self, inplace=False):
        return self.filter_inputs(
            function=lambda x: not x[SUCCESS_COL],
            how='any',
            inplace=inplace
        )

    def keep_common_failed_inputs(self, inplace=False):
        return self.filter_inputs(
            function=lambda x: not x[SUCCESS_COL],
            how='all',
            inplace=inplace
        )

    def keep_common_solved_inputs(self, inplace=False):
        return self.filter_inputs(
            function=lambda x: x[SUCCESS_COL],
            how='all',
            inplace=inplace
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

    def cactus_plot(self, cumulated=False, cactus_col=EXPERIMENT_CPU_TIME, **kwargs: dict):
        df = _make_cactus_plot_df(self, cumulated, cactus_col)

        plot = CactusPlot(df, **kwargs)
        plot.save()

        return plot.show()

    def cdf_plot(self, cumulated=False, cdf_col=EXPERIMENT_CPU_TIME, **kwargs: dict):
        df = _make_cactus_plot_df(self, cumulated, cdf_col)

        plot = CDFPlot(df, len(self.inputs), **kwargs)
        plot.save()

        return plot.show()

    def scatter_plot(self, xp_ware_x, xp_ware_y, color_col=None, scatter_col=EXPERIMENT_CPU_TIME, **kwargs):
        if xp_ware_x not in self.experiment_wares:
            raise ValueError(f'Experiment-ware xp_ware_x={xp_ware_x} does not exist.')
        if xp_ware_y not in self.experiment_wares:
            raise ValueError(f'Experiment-ware xp_ware_y={xp_ware_y} does not exist.')

        df = _make_scatter_plot_df(self, xp_ware_x, xp_ware_y, scatter_col, color_col)

        plot = ScatterPlot(df, color_col=color_col, **kwargs)
        plot.save()

        return plot.show()

    def box_plot(self, box_col=EXPERIMENT_CPU_TIME, **kwargs: dict):
        df = _make_box_plot_df(self, box_col)

        plot = BoxPlot(df, **kwargs)
        plot.save()

        return plot.show()

    def export(self, filename=None):
        if filename is None:
            return pickle.dumps(self, protocol=pickle.HIGHEST_PROTOCOL)

        if filename.split('.')[-1] == 'csv':
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
