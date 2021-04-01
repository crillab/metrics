from __future__ import annotations

import os
import unittest

import jsonpickle.ext.pandas as jsonpickle_pd

from metrics.wallet import import_campaign_data_frame, import_from_api_and_store

jsonpickle_pd.register_handlers()

from tests.test_core.json_reader import JsonReader
from metrics.wallet.dataframe.builder import *
from metrics.wallet.dataframe.dataframe import CampaignDFFilter

NAMES = [
    'AllInterval', 'Bibd', 'Blackhole', 'CarSequencing', 'ColouredQueens', 'CostasArray',
    'CoveringArray', 'Crossword', 'CryptoPuzzle', 'DeBruijnSequence', 'DiamondFree',
    'Domino',
    'Driver', 'Dubois', 'Fischer', 'GracefulGraph', 'Hanoi', 'Haystacks', 'Kakuro',
    'KnightTour', 'Knights', 'Langford', 'LatinSquare', 'MagicHexagon', 'MagicSequence',
    'MagicSquare', 'MarketSplit', 'Mixed', 'MultiKnapsack', 'Nonogram',
    'NumberPartitioning',
    'Ortholatin', 'PigeonsPlus', 'Primes', 'PropStress', 'PseudoBoolean', 'QRandom',
    'QuasiGroups', 'QueenAttacking', 'Queens', 'QueensKnights', 'RadarSurveillance',
    'Random',
    'RectPacking', 'Renault', 'RenaultMod', 'Rlfap', 'RoomMate', 'Sat', 'Scheduling',
    'SchurrLemma', 'SocialGolfers', 'SportsScheduling', 'Steiner3', 'StripPacking',
    'Subisomorphism', 'Sudoku', 'SuperSolutions', 'TravellingSalesman', 'Wwtpp'
]

INPUT = {'/home/cril/wattez/XCSP17/SuperSolutions/SuperSolutions-Sadeh-js/SuperSadeh-js-e0ddr1-1.xml.lzma'}

SET_COMMON_FAILED_INPUTS = {
    '/home/cril/wattez/XCSP17/SuperSolutions/SuperSolutions-Taillard-os15/SuperTaillard-os-15-22.xml.lzma',
    '/home/cril/wattez/XCSP17/SuperSolutions/SuperSolutions-Queens-s1/SuperQueens-12.xml.lzma',
    '/home/cril/wattez/XCSP17/SuperSolutions/SuperSolutions-Taillard-os07/SuperTaillard-os-07-26.xml.lzma',
    '/home/cril/wattez/XCSP17/SuperSolutions/SuperSolutions-Taillard-os20/SuperTaillard-os-20-17.xml.lzma',
    '/home/cril/wattez/XCSP17/SuperSolutions/SuperSolutions-Taillard-js20-15/SuperTaillard-js-20-15-15.xml'
    '.lzma',
    '/home/cril/wattez/XCSP17/SuperSolutions/SuperSolutions-Taillard-os10/SuperTaillard-os-10-11.xml.lzma',
    '/home/cril/wattez/XCSP17/SuperSolutions/SuperSolutions-Queens-s1/SuperQueens-07.xml.lzma',
    '/home/cril/wattez/XCSP17/SuperSolutions/SuperSolutions-Queens-s1/SuperQueens-02.xml.lzma',
    '/home/cril/wattez/XCSP17/SuperSolutions/SuperSolutions-Queens-s1/SuperQueens-14.xml.lzma'
}


class TestCampaignDataFrameBuilder(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, '../../data/xcsp17.json')
        jr = JsonReader(filename)
        cls.campaign = jr.campaign
        cls.campaign_df = CampaignDataFrameBuilder(cls.campaign).build_from_campaign()
        cls.campaign_df.data_frame['success'] = cls.campaign_df.data_frame.apply((lambda x: x['cpu_time'] < cls.campaign.timeout), axis=1)

        cdf = cls.campaign_df
        json_cdf = cdf.export()
        cls.campaign_df = import_campaign_data_frame(json_cdf)

    def test_data_frame(self):
        self.assertEqual(list(self.campaign_df.data_frame.columns),
                         ['input', 'experiment_ware', 'cpu_time', 'start_time', 'status', 'Constraints_arities',
                          'Constraints_distribution', 'Variables_degrees', 'family', 'date', 'success'])
        self.assertEqual(1500, len(self.campaign_df.data_frame))

    def test_delete_common_timeout(self):
        df = self.campaign_df._filter_by([CampaignDFFilter.DELETE_COMMON_TIMEOUT]).data_frame

        self.assertEqual(1173, len(df))

    def test_delete_timeout(self):
        df = self.campaign_df._filter_by([CampaignDFFilter.ONLY_SOLVED]).data_frame

        self.assertEqual(1150, len(df))

    def test_only_common_timeout(self):
        common_timeout_df = self.campaign_df._filter_by([CampaignDFFilter.ONLY_COMMON_TIMEOUT]).data_frame
        self.assertEqual(109, len(common_timeout_df.input.unique()))
        self.assertEqual(len(common_timeout_df), 327)

    def test_delete_common_solved(self):
        common_solved_df = self.campaign_df._filter_by([CampaignDFFilter.ONLY_COMMON_SOLVED]).data_frame
        full_df = self.campaign_df.data_frame
        no_common_solved_df = self.campaign_df._filter_by([CampaignDFFilter.DELETE_COMMON_SOLVED]).data_frame

        self.assertEqual(len(full_df) - len(common_solved_df), len(no_common_solved_df))

    def test_delete_solved(self):
        df = self.campaign_df._filter_by([CampaignDFFilter.ONLY_TIMEOUT]).data_frame

        self.assertEqual(350, len(df))

    def test_only_common_solved(self):
        df = self.campaign_df._filter_by([CampaignDFFilter.ONLY_COMMON_SOLVED]).data_frame

        self.assertEqual(374, len(df.input.unique()))
        self.assertEqual(1122, len(df.input))

    def test_sub_experiment_ware(self):
        df = self.campaign_df.sub_data_frame('experiment_ware', {'CHS', 'WDegCAxCD'}).data_frame
        self.assertEqual(1000, len(df))

    def test_sub_experiment_ware(self):
        df = self.campaign_df.delete_input_when(lambda x: x['cpu_time'] < 100)
        self.assertEqual(182, len(df.inputs))

    def test_sub_input(self):
        df = self.campaign_df.sub_data_frame('input',
            {'/home/cril/wattez/XCSP17/RenaultMod/RenaultMod-m1-s1/RenaultMod-18.xml.lzma'}).data_frame
        self.assertEqual(3, len(df))

    def test_add_vbs(self):
        df = self.campaign_df.add_vbew({'CHS', 'WDegCAxCD'}, 'cpu_time').data_frame
        self.assertEqual(2.138, df[(df['input'] == '/home/cril/wattez/XCSP17/SuperSolutions/SuperSolutions-Taillard-os04/SuperTaillard-os-04-26.xml.lzma') & (df['experiment_ware'] == 'vbew')]['cpu_time'].values[0])
        self.assertEqual(2000, len(df))

    def test_add_vbs_diff_10(self):
        df = self.campaign_df.add_vbew({'CHS', 'WDegCAxCD'}, 'cpu_time', diff=.1).data_frame
        self.assertEqual(532, len(df))

    def test_groupby(self):
        gb = self.campaign_df.groupby('family')
        names = [x.name.split('>')[-1] for x in gb]
        self.assertEqual(names, NAMES)

        sub = next(sub for sub in gb if sub.name.split('>')[-1] == 'SuperSolutions')
        self.assertEqual(8, len(sub._filter_by([CampaignDFFilter.ONLY_COMMON_SOLVED]).data_frame.input.unique()))

        df_no_common_solved_no_out = sub._filter_by([
            CampaignDFFilter.DELETE_COMMON_SOLVED,
            CampaignDFFilter.ONLY_SOLVED,
        ]).data_frame
        self.assertEqual(2, len(df_no_common_solved_no_out))

        self.assertEqual(INPUT, set(df_no_common_solved_no_out['input']))

        self.assertEqual(SET_COMMON_FAILED_INPUTS, set(sub._filter_by([CampaignDFFilter.ONLY_COMMON_TIMEOUT]).data_frame.input.unique()))


class TestCampaignDataFrameBuilderVBS(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, '../../data/xcsp17.json')
        jr = JsonReader(filename)
        cls.campaign = jr.campaign
        cls.campaign_df = CampaignDataFrameBuilder(cls.campaign).build_from_campaign()\
            .add_vbew({'CHS', 'WDegCAxCD'}, 'cpu_time')
        cls.campaign_df.data_frame['success'] = cls.campaign_df.data_frame.apply((lambda x: x['cpu_time'] < cls.campaign.timeout), axis=1)

    def test_get_xpware_name_list(self):
        self.assertCountEqual(self.campaign_df.xp_ware_names, ['ExplorationLuby', 'vbew', 'WDegCAxCD', 'CHS'])

    def test_delete_common_solved(self):
        common_solved_df = self.campaign_df._filter_by([CampaignDFFilter.ONLY_COMMON_SOLVED]).data_frame
        full_df = self.campaign_df.data_frame
        no_common_solved_df = self.campaign_df._filter_by([CampaignDFFilter.DELETE_COMMON_SOLVED]).data_frame

        self.assertEqual(len(full_df) - len(common_solved_df), len(no_common_solved_df))

    def test_groupby(self):
        gb = self.campaign_df.groupby('family')
        names = [x.name.split('>')[-1] for x in gb]
        self.assertEqual(names, NAMES)

        sub = next(sub for sub in gb if sub.name.split('>')[-1] == 'SuperSolutions')
        self.assertEqual(8, len(sub._filter_by([CampaignDFFilter.ONLY_COMMON_SOLVED]).data_frame.input.unique()))

        df_no_common_solved_no_out = sub._filter_by([
            CampaignDFFilter.DELETE_COMMON_SOLVED,
            CampaignDFFilter.ONLY_SOLVED,
        ]).data_frame
        self.assertEqual(3, len(df_no_common_solved_no_out))

        self.assertEqual(INPUT, set(df_no_common_solved_no_out['input']))

        self.assertEqual(SET_COMMON_FAILED_INPUTS, set(sub._filter_by([CampaignDFFilter.ONLY_COMMON_TIMEOUT]).data_frame.input.unique()))


class TestCampaignDataFrameVbew(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, '../../data/xcsp18.json')

        campaign = import_from_api_and_store('', filename)
        cls.analysis = Analysis(campaign=campaign)

    def test_vbew(self):
        VBS_SOLVERS = {
            'WDegCAxCD',
            'CHS',
            'Activity',
            'DDegOnDom',
            'Impact',
        }

        df = self.analysis.add_vbew(VBS_SOLVERS).campaign_df.data_frame

        self.assertEqual(2493, len(df))


class TestCampaignDataFrameBuilderSubWare(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, '../../data/xcsp17.json')
        jr = JsonReader(filename)
        cls.campaign = jr.campaign
        cls.campaign_df = CampaignDataFrameBuilder(cls.campaign).build_from_campaign().sub_data_frame(
            'experiment_ware',
            {'CHS', 'WDegCAxCD'}
        )
        cls.campaign_df.data_frame['success'] = cls.campaign_df.data_frame.apply((lambda x: x['cpu_time'] < cls.campaign.timeout), axis=1)

    def test_get_xpware_name_list(self):
        self.assertCountEqual(self.campaign_df.xp_ware_names, ['WDegCAxCD', 'CHS'])

    def test_delete_common_solved(self):
        common_solved_df = self.campaign_df._filter_by([CampaignDFFilter.ONLY_COMMON_SOLVED]).data_frame
        full_df = self.campaign_df.data_frame
        no_common_solved_df = self.campaign_df._filter_by([CampaignDFFilter.DELETE_COMMON_SOLVED]).data_frame

        self.assertEqual(len(full_df) - len(common_solved_df), len(no_common_solved_df))

    def test_groupby(self):
        gb = self.campaign_df.groupby('family')
        names = [x.name.split('>')[-1] for x in gb]
        self.assertEqual(names, NAMES)

        sub = next(sub for sub in gb if sub.name.split('>')[-1] == 'SuperSolutions')
        self.assertEqual(8, len(sub._filter_by([CampaignDFFilter.ONLY_COMMON_SOLVED]).data_frame.input.unique()))

        df_no_common_solved_no_out = sub._filter_by([
            CampaignDFFilter.DELETE_COMMON_SOLVED,
            CampaignDFFilter.ONLY_SOLVED,
        ]).data_frame
        self.assertEqual(1, len(df_no_common_solved_no_out))

        self.assertEqual(INPUT, set(df_no_common_solved_no_out['input']))

        self.assertEqual(SET_COMMON_FAILED_INPUTS, set(sub._filter_by([CampaignDFFilter.ONLY_COMMON_TIMEOUT]).data_frame.input.unique()))


if __name__ == '__main__':
    unittest.main()
