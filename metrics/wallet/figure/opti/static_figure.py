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

from metrics.wallet.figure.abstract_figure import Table

from math import isnan
from bisect import bisect_right
from pandas import Series, DataFrame
from math import log
from itertools import product


def minmax_obj_to_max(row):
    coeff = 1 if row['objective'] == 'max' else -1
    return [coeff * int(x) for x in row['bound_list']]


def build_xp(row, s):
    ts = row.timestamp_list
    index = max(bisect_right(ts, s) - 1, 0) if len(ts) else None
    timestamp = ts[index] if index is not None else None
    timestamp = None if timestamp is None or timestamp > s else timestamp
    best_bound = row.bound_list[index] if timestamp is not None else None

    return Series({
        'input': row.input,
        'experiment_ware': row.experiment_ware,
        'timeout': s,
        'status': row.success and timestamp is not None and timestamp <= row.cpu_time,
        'timestamp': timestamp,
        'ba': best_bound,
    })


def computer_er(x):
    if x['ba'] is None or isnan(x['ba']):
        return 1
    if x['bA'] == x['ba']:
        return 10000
    if x['maxA'] == x['minA']:
        return 1

    return (x['maxA'] - x['minA']) / (x['bA'] - x['ba'])


def compute_wf(df, S, wf):
    wf = wf.copy()
    summ = sum(wf)
    removed = 0

    for i, s in enumerate(S):
        if not df[df.timeout == s].ba.isnull().all():
            break
        removed += wf[i]
        wf[i] = 0

    for i, s in enumerate(S[0:-2]):
        if df[df.timeout == s].status.all():
            wf[i + 1:] = [0] * (len(S) - i - 1)

    coeff = summ / (summ - removed)

    return df.timeout.map({s: w * coeff for s, w in zip(S, wf)})


def agg_input(df, S, wf):
    minA = df.bound_list.apply(lambda x: x[0] if len(x) else None).min()
    maxA = df.bound_list.apply(lambda x: x[-1] if len(x) else None).max()

    if isnan(minA):
        return None

    df = DataFrame([build_xp(row, s) for row, s in product(df.itertuples(), S)])

    df['minA'] = minA
    df['maxA'] = maxA
    df['bA'] = df.timeout.map(df.groupby('timeout')['ba'].max())
    df['domine'] = df['ba'] == df['bA']
    df['er'] = df.apply(computer_er, axis=1)
    df['sr'] = df.er.apply(lambda x: min(log(x, 10), 4) / 4)
    df['wf'] = compute_wf(df, S, wf)

    return df


def cop_stats(df, T, S, alpha, wf):
    df['bound_list'] = df.apply(minmax_obj_to_max, axis=1)
    df = df.groupby('input', group_keys=False).apply(lambda x: agg_input(x, S, wf))

    df['score'] = df.domine * alpha + df.sr * (1 - alpha)

    return df


def scoring_christophe_gilles(df):
    return sum(df.wf * df.score)


def scoring_classic(df):
    return sum(df.domine) + sum(df.status) * 2


class FullOptiStat(Table):

    def __init__(self, campaign_df, T, S, alpha, wf, **kwargs):
        super().__init__(campaign_df, **kwargs)
        self._T = T
        self._S = S
        self._alpha = alpha
        self._wf = wf

    def get_data_frame(self):
        return cop_stats(self._campaign_df.data_frame.copy(), self._T, self._S, self._alpha, self._wf)
