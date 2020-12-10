from __future__ import annotations

import os
import unittest

import jsonpickle.ext.pandas as jsonpickle_pd


jsonpickle_pd.register_handlers()

from metrics.wallet import Analysis


class TestFullCampaign(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        filename = 'tests/test_wallet/full_campaign_data/campaign/config/metrics_scalpel.yml'
        cls.analysis = Analysis(input_file=filename)

    def test_analysis_columns(self):
        self.assertFalse('experiment_ware_experiment' in self.analysis.campaign_df.data_frame.columns)
        self.assertFalse('input_input' in self.analysis.campaign_df.data_frame.columns)
        self.assertFalse('experiment_ware_xpware' in self.analysis.campaign_df.data_frame.columns)
