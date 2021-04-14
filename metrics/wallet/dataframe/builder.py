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
from typing import Set, Callable, Any, List, Tuple
from warnings import warn

from pandas import DataFrame
from itertools import product

from metrics.core.model import Campaign
from metrics.core.constants import EXPERIMENT_CPU_TIME, SUCCESS_COL, INPUT_NAME, EXPERIMENT_INPUT, XP_WARE_NAME, \
    EXPERIMENT_XP_WARE, SUFFIX_EXPERIMENT, SUFFIX_INPUT, SUFFIX_XP_WARE, MISSING_DATA_COL, XP_CONSISTENCY_COL, \
    ERROR_COL, \
    TIMEOUT_COL, INPUT_CONSISTENCY_COL
from metrics.scalpel import read_campaign
from metrics.wallet.figure.dynamic_figure import CactusPlotly, ScatterPlotly, BoxPlotly, CDFPlotly
from metrics.wallet.figure.static_figure import CactusMPL, ScatterMPL, BoxMPL, StatTable, ContributionTable, \
    ErrorTable, PivotTable, Description, CDFMPL


def find_best_cpu_time_input(df):
    s = df[EXPERIMENT_CPU_TIME]
    return df[s == s.min()]


class Analysis:

    def __init__(self, input_file: str = None, data_frame: DataFrame = None,
                 is_consistent_by_xp: Callable[[Any], bool] = None,
                 is_consistent_by_input: Callable[[Any], bool] = None,
                 is_success: Callable[[Any], bool] = None):

        if data_frame is not None:
            self._data_frame = data_frame
            self.check_success(is_success)
            self.check_missing_experiments(
                inputs=self.inputs,
                experiment_wares=self.experiment_wares
            )
        else:
            campaign, config = read_campaign(input_file)

            self._data_frame = DataFrameBuilder(campaign).build_from_campaign()
            self._data_frame[TIMEOUT_COL] = campaign.timeout
            self._data_frame[ERROR_COL] = False

            self.check_success(config.get_is_success() if is_success is None else is_success)

            self.check_missing_experiments(
                inputs=campaign.get_input_set().get_input_names(),
                experiment_wares=campaign.get_experiment_ware_names()
            )

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
        self._data_frame[SUCCESS_COL] = (self._data_frame[SUCCESS_COL]) & (~self._data_frame[ERROR_COL])

    def check_success(self, is_success: Callable[[Any], bool]):
        if is_success is None:
            return
        self._data_frame[SUCCESS_COL] = self._data_frame.apply(is_success, axis=1)

    def check_missing_experiments(self, inputs: List[str], experiment_wares: List[str]):
        theoretical_df = DataFrame(product(inputs, experiment_wares), columns=[EXPERIMENT_INPUT, EXPERIMENT_XP_WARE])

        self._data_frame[MISSING_DATA_COL] = False
        self._data_frame = self._data_frame.join(
            theoretical_df.set_index([EXPERIMENT_INPUT, EXPERIMENT_XP_WARE]), how='right',
            on=[EXPERIMENT_INPUT, EXPERIMENT_XP_WARE])
        self._data_frame[MISSING_DATA_COL] = self._data_frame[MISSING_DATA_COL].fillna(True)

        self._update_error_and_success_cols(self._data_frame[MISSING_DATA_COL])

        n_missing = self._data_frame[MISSING_DATA_COL].sum()

        if n_missing > 0:
            warn(f'{n_missing} experiments are missing and have been added as unsuccessful.')

    def check_xp_consistency(self, is_consistent: Callable[[Any], bool]):
        if is_consistent is None:
            return

        self._data_frame[XP_CONSISTENCY_COL] = self._data_frame.apply(is_consistent, axis=1)

        inconsistency = ~self._data_frame[XP_CONSISTENCY_COL]

        self._update_error_and_success_cols(inconsistency)

        n_inconsistencies = inconsistency.sum()

        if n_inconsistencies > 0:
            warn(f'{n_inconsistencies} experiments are inconsistent and are declared as unsuccessful.')

    def check_input_consistency(self, is_consistent: Callable[[Any], bool]):
        if is_consistent is None:
            return

        s = self._data_frame.groupby(EXPERIMENT_INPUT).apply(is_consistent)

        inconsistent_inputs = set(s[~s].index)

        if len(inconsistent_inputs) > 0:
            warn(
                f'{len(inconsistent_inputs)} inputs are inconsistent and linked experiments are now declared as unsuccessful.')

            self._data_frame[INPUT_CONSISTENCY_COL] = ~self._data_frame[EXPERIMENT_INPUT].isin(inconsistent_inputs)
            self._update_error_and_success_cols(~self._data_frame[INPUT_CONSISTENCY_COL])

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
        return self.add_data_frame(analysis.data_frame, is_consistent_by_xp, is_consistent_by_input, is_success)

    def add_data_frame(self, data_frame,
                       is_consistent_by_xp: Callable[[Any], bool] = None,
                       is_consistent_by_input: Callable[[Any], bool] = None,
                       is_success: Callable[[Any], bool] = None):
        return self.__class__(
            data_frame=self._data_frame.append(data_frame, ignore_index=True),
            is_consistent_by_xp=is_consistent_by_xp,
            is_consistent_by_input=is_consistent_by_input,
            is_success=is_success
        )

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

    def filter_analysis(self, column, sub_set) -> Analysis:
        """
        Filters the dataframe in function of sub set of authorized values for a given column.
        @param column: column where  to keep the sub set of values.
        @param sub_set: the sub set of authorised values.
        @return: the filtered dataframe in a new instance of Analysis.
        """
        return self.__class__(self._data_frame[self._data_frame[column].isin(sub_set)])

    def add_vbew(self, xp_ware_set=None, opti_col=EXPERIMENT_CPU_TIME, minimize=True, vbew_name='vbew',
                 diff=0) -> Analysis:
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

        df_vbs = df_vbs.groupby(EXPERIMENT_INPUT).apply(lambda x: _vbew_agg(x, opti_col, minimize, diff)).dropna(
            how='all') \
            .assign(experiment_ware=lambda x: vbew_name)

        df = df[df[EXPERIMENT_INPUT].isin(df_vbs[EXPERIMENT_INPUT])]
        df = pd.concat([df, df_vbs], ignore_index=True)

        self._vbew_names.add(vbew_name)

        return self.build_data_frame(df)

    def groupby(self, column) -> List[Analysis]:
        """
        Makes a group by a given column.
        @param column: column where to applu the groupby.
        @return: a list of Analysis with each group.
        """
        return [
            self.__class__(campaign_df=cdf) for cdf in self._campaign_df.groupby(column)
        ]

    def get_all_experiment_ware_pairs(self) -> List[Analysis]:
        xpw = self.campaign_df.xp_ware_names

        return [
            self.sub_analysis('experiment_ware', [xpw[i], j]) for i in range(len(xpw) - 1) for j in xpw[i + 1:]
        ]

    def normalize_by(self, xp_ware, on) -> Analysis:
        return self.__class__(campaign_df=self._campaign_df.normalize_by(xp_ware, on))

    def get_only_failed(self):
        return self.__class__(campaign_df=self._campaign_df.get_only_failed())

    def get_only_success(self):
        return self.__class__(campaign_df=self._campaign_df.get_only_success())

    def get_only_common_failed(self):
        return self.__class__(campaign_df=self._campaign_df.get_only_common_failed())

    def get_only_common_success(self):
        return self.__class__(campaign_df=self._campaign_df.get_only_common_success())

    def delete_common_failed(self):
        return self.__class__(campaign_df=self._campaign_df.delete_common_failed())

    def delete_common_success(self):
        return self.__class__(campaign_df=self._campaign_df.delete_common_success())

    def delete_input_when(self, f):
        return self.__class__(campaign_df=self._campaign_df.delete_input_when(f))

    def describe(self, **kwargs: dict):
        return Description(self._campaign_df, **kwargs).get_description()

    def get_cactus_plot(self, dynamic: bool = False, **kwargs: dict):
        return (CactusPlotly(self._campaign_df, **kwargs) if dynamic else CactusMPL(self._campaign_df,
                                                                                    **kwargs)).get_figure()

    def get_scatter_plot(self, dynamic: bool = False, **kwargs: dict):
        return (ScatterPlotly(self._campaign_df, **kwargs) if dynamic else ScatterMPL(self._campaign_df,
                                                                                      **kwargs)).get_figure()

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

    @property
    def campaign(self):
        """

        @return: the campaign associated to this builder.
        """
        return self._campaign

    def build_from_campaign(self) -> DataFrame:
        """
        Builds a campaign dataframe directly from the original campaign.
        @return: the builded campaign dataframe.
        """
        experiment_wares_df = self._make_experiment_wares_df()
        inputs_df = self._make_inputs_df()
        experiments_df = self._make_experiments_df()

        return experiments_df \
            .join(inputs_df.set_index(INPUT_NAME), on=EXPERIMENT_INPUT, lsuffix=SUFFIX_EXPERIMENT, rsuffix=SUFFIX_INPUT,
                  how='inner') \
            .join(experiment_wares_df.set_index(XP_WARE_NAME),
                  on=EXPERIMENT_XP_WARE, lsuffix=SUFFIX_EXPERIMENT, rsuffix=SUFFIX_XP_WARE, how='inner'
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
