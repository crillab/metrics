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

import math
import pickle
from typing import List
import warnings

from metrics.wallet.plot import LinePlot, CDFPlot, ScatterPlot, BoxPlot

from pandas import DataFrame
from itertools import product
import pandas as pd
from deprecated import deprecated
from types import SimpleNamespace

from metrics.core.model import Campaign
from metrics.core.constants import *
from metrics.scalpel import read_campaign

warnings.formatwarning = lambda msg, *args, **kwargs: str(msg) + '\n'


def export_data_frame(data_frame, output=None, commas_for_number=False, dollars_for_number=False, col_dict=None,
                      **kwargs):
    if output is None:
        return data_frame

    df = data_frame

    if col_dict is not None:
        df = df[col_dict.keys()].rename(columns=col_dict)

    if commas_for_number:
        df = df.applymap(lambda x: f"{x:,}")

    if dollars_for_number:
        df = df.applymap(lambda x: f"${x}$")

    ext = output.split('.')[-1]

    if ext == 'tex':
        with open(output, 'w') as file:
            df.fillna('').to_latex(
                buf=file,
                escape=False,
                index_names=False,
                #bold_rows=True,
                **kwargs
            )
    elif ext == 'csv':
        with open(output, 'w') as file:
            df.fillna('').to_csv(
                buf=file,
                **kwargs
            )
    elif ext == 'xls' or ext == 'xlsx':
        with open(output, 'w') as file:
            df.fillna('').to_excel(
                buf=file,
                **kwargs
            )
    else:
        raise ValueError('Only .tex|csv|xls(x) extensions are accepted.')

    return data_frame


class BasicAnalysis:

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
    @deprecated(version='1.0.4', reason="This function will be removed for the 2.0.0 version")
    def campaign_df(self):
        return SimpleNamespace(**{
            'data_frame': self._data_frame
        })

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

    def check(self, is_success=None, is_consistent_by_xp=None, is_consistent_by_input=None, inputs=None,
              experiment_wares=None):
        self.check_success(is_success)
        self.check_missing_experiments(inputs, experiment_wares)
        self.check_xp_consistency(is_consistent_by_xp)
        self.check_input_consistency(is_consistent_by_input)

    def _check_global_success(self):
        self._data_frame[SUCCESS_COL] = self._data_frame.apply(
            lambda x: x[USER_SUCCESS_COL] and not (x[MISSING_DATA_COL]) and x[XP_CONSISTENCY_COL] and
                      x[INPUT_CONSISTENCY_COL],
            axis=1
        )

        self._data_frame[EXPERIMENT_CPU_TIME] = self._data_frame.apply(
            lambda x: x[EXPERIMENT_CPU_TIME] if x[USER_SUCCESS_COL] else x[TIMEOUT_COL],
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

    def filter_analysis(self, function, inplace=False) -> BasicAnalysis:
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

    def remove_experiment_wares(self, experiment_wares, inplace=False) -> BasicAnalysis:
        """
        Filters the dataframe in function of sub set of authorized values for a given column.
        @param column: column where  to keep the sub set of values.
        @param sub_set: the sub set of authorised values.
        @return: the filtered dataframe in a new instance of Analysis.
        """
        if not inplace:
            return self.copy().remove_experiment_wares(experiment_wares, inplace=True)

        return self.filter_analysis(lambda x: x[EXPERIMENT_XP_WARE] not in experiment_wares, inplace)

    def keep_experiment_wares(self, experiment_wares, inplace=False) -> BasicAnalysis:
        """
        Filters the dataframe in function of sub set of authorized values for a given column.
        @param column: column where  to keep the sub set of values.
        @param sub_set: the sub set of authorised values.
        @return: the filtered dataframe in a new instance of Analysis.
        """
        return self.filter_analysis(lambda x: x[EXPERIMENT_XP_WARE] in experiment_wares, inplace)

    def filter_inputs(self, function, how='all', inplace=False) -> BasicAnalysis:
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

    def apply_on_groupby(self, by, func, inplace=False):
        if not inplace:
            return self.copy().apply_on_groupby(by, func, inplace=True)

        self._data_frame = self._data_frame.groupby(
            by
        ).apply(func).reset_index(drop=True)

        return self

    def all_experiment_ware_pair_analysis(self) -> List[BasicAnalysis]:
        xpw = self.experiment_wares

        return [
            self.keep_experiment_wares([xpw[i], j]) for i in range(len(xpw) - 1) for j in
            xpw[i + 1:]
        ]

    def all_xp_ware_pair_analysis(self) -> List[BasicAnalysis]:
        return self.all_experiment_ware_pair_analysis()

    def groupby(self, column) -> List[BasicAnalysis]:
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

    def line_plot(self, index, column, values, **kwargs: dict):
        df = self.pivot_table(
            index=index,
            columns=column,
            values=values
        )

        s = df.iloc[-1].sort_values(ascending=False).index
        df = df[s]

        plot = LinePlot(df, **kwargs)
        plot.save()

        return plot.show()

    def export(self, filename=None):
        if filename is None:
            return pickle.dumps(self._data_frame, protocol=pickle.HIGHEST_PROTOCOL)

        if filename.split('.')[-1] == 'csv':
            return self._data_frame.to_csv(filename, index=False)
        else:
            with open(filename, 'wb') as file:
                return pickle.dump(self._data_frame, file, protocol=pickle.HIGHEST_PROTOCOL)

    @classmethod
    def import_from_file(cls, filename):
        with open(filename, 'rb') as file:
            if filename.split('.')[-1] == 'csv':
                return cls(data_frame=pd.read_csv(file))
            return cls(data_frame=pickle.load(file))


def _is_none_or_nan(x):
    return x is None or math.isnan(x)


def _make_list(l):
    if isinstance(l, list):
        return l
    if l is None:
        return []
    return [l]


def _default_explode(df, samp):
    d = df.iloc[0].to_dict()
    times = _make_list(d.pop('timestamp_list'))
    bounds = _make_list(d.pop('bound_list'))
    if d.pop('objective') == 'min':
        bounds = [-x for x in bounds]

    if len(bounds) != len(times):
        raise Exception('Bound list length and time list length must be equals.')

    l = []
    i = 0
    for j in range(len(bounds)):
        while times[j] > samp[i]:
            d2 = d.copy()
            d2['status'] = d2['status'] if d2['cpu_time'] < samp[i] else 'INCOMPLETE'
            d2['success'] = d2['status'] == 'COMPLETE'
            d2['cpu_time'] = times[j - 1] if j - 1 >= 0 else samp[i]
            d2['timeout'] = samp[i]
            d2['best_bound'] = bounds[j - 1] if j - 1 >= 0 else None
            l.append(d2)
            i += 1

    for j in range(i, len(samp)):
        d2 = d.copy()
        d2['cpu_time'] = times[-1] if len(times) > 0 else samp[j]
        d2['timeout'] = samp[j]
        d2['best_bound'] = bounds[-1] if len(times) > 0 else None
        l.append(d2)

    return pd.DataFrame(l)


def _norm(minB, maxB, x):
    if maxB == minB:
        return 1 if x == maxB else 0
    if _is_none_or_nan(x):
        return 0
    return (float(x) - minB) / (float(maxB) - minB)


def _borda(x, df):
    summ = 0

    for _, row in df.iterrows():
        if row['experiment_ware'] == x['experiment_ware'] or _is_none_or_nan(x['best_bound']):
            continue

        if _is_none_or_nan(row['best_bound']):
            summ += 1
            continue

        if x['best_bound'] != row['best_bound']:
            summ += 1 if x['best_bound'] > row['best_bound'] else 0
            continue

        if x['status'] == row['status']:
            summ += row['cpu_time'] / (x['cpu_time'] + row['cpu_time'])
            continue

        summ += 1 if x['status'] == 'COMPLETE' else 0

    return summ


def optimality_score(x, min_b, max_b, df):
    return 1 if x['success'] else 0


def dominance_score(x, min_b, max_b, df):
    return 1 if x['best_bound'] == max_b else 0


def norm_bound_score(x, min_b, max_b, df):
    return _norm(min_b, max_b, x['best_bound'])


def borda_score(x, min_b, max_b, df):
    return _borda(x, df)


DEFAULT_SCORE_METHODS = {
    'optimality': optimality_score,
    'dominance': dominance_score,
    'norm_bound': norm_bound_score,
    'borda': borda_score
}


def _compute_scores(df, default_solver, score_map):
    min_b = df.best_bound.min()
    max_b = df.best_bound.max()

    for col, lbd in score_map.items():
        df[col] = df.apply(lambda x: lbd(x, min_b, max_b, df), axis=1)

    if default_solver is not None:
        def_s = df[df.experiment_ware == default_solver].iloc[0]

        for col in score_map:
            df[f'{col}_less_def'] = df[col] - def_s[col]

    return df


def _input_agg(df, col):
    d = df.iloc[0].to_dict()
    d2 = {
        'experiment_ware': d['experiment_ware'],
        'timeout': d['timeout'],
        col: df[col].mean()
    }
    return pd.Series(d2)


class OptiAnalysis(BasicAnalysis):

    def __init__(self, input_file: str = None, data_frame: DataFrame = None, basic_analysis: BasicAnalysis = None, func=_default_explode, samp=None):
        if input_file is not None or basic_analysis is not None:
            super().__init__(
                input_file,
                None if basic_analysis is None else basic_analysis.data_frame
            )
            self._explode_experiments(func, samp)
        elif data_frame is not None:
            self._data_frame = data_frame
        else:
            raise AttributeError('input_file or data_frame or basic_analysis needs to be given.')

    def _explode_experiments(self, func, samp=None):
        self.apply_on_groupby(
            by=[EXPERIMENT_INPUT, EXPERIMENT_XP_WARE],
            func=lambda df: func(
                df,
                [self.data_frame.timeout.max()] if samp is None else samp
            ),
            inplace=True
        )

    def compute_scores(self, default_solver=None, score_map=DEFAULT_SCORE_METHODS):
        self.apply_on_groupby(
            by=['input', 'timeout'],
            func=lambda df: _compute_scores(df, default_solver, score_map),
            inplace=True
        )

    def opti_line_plot(self, col, **kwargs):
        return self.apply_on_groupby(
            by=['experiment_ware', 'timeout'],
            func=lambda df: _input_agg(df, col)
        ).line_plot(
            index='timeout',
            column='experiment_ware',
            values=col,
            **kwargs
        )


def find_best_cpu_time_input(df):
    return df.sort_values(by=[SUCCESS_COL, EXPERIMENT_CPU_TIME], ascending=[False, True]).iloc[0]


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
    sli = sli.sort_values(by=[SUCCESS_COL, EXPERIMENT_CPU_TIME], ascending=[False, True])
    first = sli.iloc[0]
    second = sli.iloc[1]
    index = [EXPERIMENT_XP_WARE, EXPERIMENT_CPU_TIME, 'unique', 'second_time']

    if first[SUCCESS_COL]:
        return pd.Series(
            [first[EXPERIMENT_XP_WARE], first[EXPERIMENT_CPU_TIME],
             not second[SUCCESS_COL], second[EXPERIMENT_CPU_TIME] if second[SUCCESS_COL] else 1000000],
            index=index)

    return pd.Series([None, None, False, None], index=index)


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

    df[EXPERIMENT_CPU_TIME] = df.apply(lambda x: x['timeout'] if not x['success'] else x['cpu_time'], axis=1)

    df1 = df.pivot_table(
        index=EXPERIMENT_INPUT,
        columns=EXPERIMENT_XP_WARE,
        values=scatter_col,
        fill_value=analysis.data_frame[TIMEOUT_COL].max()
    )[[xp_ware_x, xp_ware_y]]

    if color_col is not None:
        df2 = df.groupby(EXPERIMENT_INPUT).apply(lambda dff: set(dff[color_col]))
        df1[color_col] = df2.apply(lambda x: list(x)[0] if len(x) == 1 else x)

    return df1


def _make_box_plot_df(analysis, box_by, box_col):
    return analysis.data_frame.pivot(
        columns=box_by,
        index=EXPERIMENT_INPUT,
        values=box_col
    )


class DecisionAnalysis(BasicAnalysis):

    def __init__(self, input_file: str = None, data_frame: DataFrame = None, basic_analysis: BasicAnalysis = None):
        if input_file is not None:
            super().__init__(input_file, data_frame)
        elif data_frame is not None:
            self._data_frame = data_frame
        elif basic_analysis is not None:
            self._data_frame = basic_analysis.data_frame
        else:
            raise AttributeError('input_file or data_frame or basic_analysis needs to be given.')

        # test if the naalysis is in conformity

    def add_virtual_experiment_ware(self, function=find_best_cpu_time_input, xp_ware_set=None, name='vbew') -> BasicAnalysis:
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

    def stat_table(self, par=[1, 2, 10], **kwargs):
        stats = self._data_frame.groupby(EXPERIMENT_XP_WARE).apply(
            lambda df: _compute_cpu_time_stats(df, par))
        common = self.keep_common_solved_inputs().data_frame
        if len(common) > 0:
            stats[STAT_TABLE_COMMON_COUNT] = common.groupby(EXPERIMENT_XP_WARE).apply(
                lambda df: df[SUCCESS_COL].sum())
            stats[STAT_TABLE_COMMON_SUM] = common.groupby(EXPERIMENT_XP_WARE).apply(
                lambda df: df.apply(lambda x: _cpu_time_stat(x, 1), axis=1).sum())
        else:
            stats[STAT_TABLE_COMMON_COUNT] = stats[STAT_TABLE_COMMON_SUM] = 0
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
            sub = contrib_raw[(contrib_raw['second_time'] - contrib_raw.cpu_time) >= delta]
            contrib[f'vbew {delta}s'] = sub.groupby(EXPERIMENT_XP_WARE).cpu_time.count()

        contrib['contribution'] = contrib_raw.groupby(EXPERIMENT_XP_WARE).unique.sum()

        return export_data_frame(
            data_frame=contrib.fillna(0).astype(int).sort_values(['vbew simple', 'contribution'],
                                                                 ascending=[False, False]),
            **kwargs
        )

    def cactus_plot(self, cumulated=False, cactus_col=EXPERIMENT_CPU_TIME, **kwargs: dict):
        df = _make_cactus_plot_df(self, cumulated, cactus_col)

        plot = LinePlot(df, **kwargs)
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

    def box_plot(self, box_col=EXPERIMENT_CPU_TIME, box_by=EXPERIMENT_XP_WARE, **kwargs: dict):
        df = _make_box_plot_df(self, box_by, box_col)

        plot = BoxPlot(df, **kwargs)
        plot.save()

        return plot.show()


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
