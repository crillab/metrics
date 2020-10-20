from __future__ import annotations

import os
import unittest

import jsonpickle.ext.pandas as jsonpickle_pd


jsonpickle_pd.register_handlers()

from tests.test_core.json_reader import JsonReader
from metrics.wallet.dataframe.builder import Analysis

import re


class TestAnalysis(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, '../../data/xcsp17.json')
        jr = JsonReader(filename)
        campaign = jr.campaign

        cls.analysis = Analysis(campaign=campaign)

    def test_analysis(self):
        self.assertEqual(1500, len(self.analysis.campaign_df.data_frame))

    def test_map(self):
        rx = re.compile("^/home/cril/wattez/XCSP17/(.*?)/")
        self.analysis.map('family', lambda x: rx.findall(x['input'])[0])
        self.assertEqual('SuperSolutions', self.analysis.campaign_df.data_frame['family'][0])
