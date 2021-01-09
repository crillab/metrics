from __future__ import annotations

import unittest

import jsonpickle.ext.pandas as jsonpickle_pd

from metrics.wallet import import_analysis_from_file, scoring_classic, scoring_christophe_gilles, Analysis, AnalysisOpti
from metrics.wallet.figure.opti.static_figure import scoring_borda

jsonpickle_pd.register_handlers()

class TestCop(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open('data/cop_campaign_diff_opti', 'rb') as file:
            cls.analysis = import_analysis_from_file(file=file)

        cls.analysis = AnalysisOpti(campaign=cls.analysis.campaign_df.campaign)


    def test_diff_opti(self):
        df = self.analysis.campaign_df.data_frame
        self.assertEqual(12, len(df[df.error]))
