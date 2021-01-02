from __future__ import annotations

import unittest

import jsonpickle.ext.pandas as jsonpickle_pd

from metrics.wallet import import_analysis_from_file, scoring_classic, scoring_christophe_gilles
from metrics.wallet.figure.opti.static_figure import scoring_borda

jsonpickle_pd.register_handlers()



class TestCop(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open('data/cop_campaign', 'rb') as file:
            cls.analysis = import_analysis_from_file(file=file).sub_analysis('experiment_ware', {
                'WDegCAxCD',
                'WDegCAxCD+gap_exp',
                'WDegCAxCD+gap_prev',
            })

    def test_cop(self):
        T = 120
        alpha = 0.5
        S = [1, 10, 100]

        df = self.analysis.get_opti_stat_table(
            T=T,
            S=S,
            alpha=alpha,
            wf=[1] * len(S),
            scorings=[
                scoring_classic,
                scoring_christophe_gilles,
                scoring_borda,
            ],
            order_by=['scoring_classic'],
            groupby=['experiment_ware'],
        )

        print(df)
