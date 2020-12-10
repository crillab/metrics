from __future__ import annotations

import unittest

import jsonpickle.ext.pandas as jsonpickle_pd


jsonpickle_pd.register_handlers()

from metrics.wallet import Analysis


class TestFullCampaign(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.analysis = Analysis(input_file='full_campaign_data/campaign/config/metrics_scalpel.yml')

    def test_analysis_columns(self):
        self.assertFalse('experiment_ware_experiment' in self.analysis.campaign_df.data_frame.columns)
        self.assertFalse('input_input' in self.analysis.campaign_df.data_frame.columns)
        self.assertFalse('experiment_ware_xpware' in self.analysis.campaign_df.data_frame.columns)
