import os
import unittest

import matplotlib.pyplot as plt

from tests.test_core.json_reader import JsonReader
from metrics.wallet.dataframe.builder import CampaignDataFrameBuilder, Analysis
from metrics.wallet.figure.static_figure import LINE_STYLES, ContributionTable, DEFAULT_COLORS, ErrorTable, StatTable


class MyTestCase(unittest.TestCase):
    STAT_TABLE_RESULT_NO_VBS = {
        'CHS': {'common count': 374,
                'common sum': 21656,
                'count': 380,
                'sum': 66237,
                'total': 500,
                'uncommon count': 6},
        'ExplorationLuby': {'common count': 374,
                            'common sum': 22161,
                            'count': 389,
                            'sum': 38602,
                            'total': 500,
                            'uncommon count': 15},
        'WDegCAxCD': {'common count': 374,
                      'common sum': 27034,
                      'count': 381,
                      'sum': 67638,
                      'total': 500,
                      'uncommon count': 7}}

    STAT_TABLE_RESULT_VBS = {
        "CHS": {
            "count": 380,
            "sum": 66237,
         'total': 500,
            "common count": 374,
            "common sum": 21656,
            "uncommon count": 6
        },
        "ExplorationLuby": {
            "count": 389,
            "sum": 38602,
         'total': 500,
            "common count": 374,
            "common sum": 22161,
            "uncommon count": 15
        },
        "WDegCAxCD": {
            "count": 381,
            "sum": 67638,
         'total': 500,
            "common count": 374,
            "common sum": 27034,
            "uncommon count": 7
        },
        "vbew": {
            "count": 387,
            "sum": 39302,
         'total': 500,
            "common count": 374,
            "common sum": 15317,
            "uncommon count": 13
        }
    }

    SUB_INPUT_SET = [
        '/home/cril/wattez/XCSP17/MagicSquare/MagicSquare-m1-gp/MagicSquare-9-f10-20.xml.lzma',
        '/home/cril/wattez/XCSP17/Wwtpp/Wwtpp-ord-s1/Wwtpp-ord-ex06460.xml.lzma',
        '/home/cril/wattez/XCSP17/Hanoi/Hanoi-m1-s1/Hanoi-08.xml.lzma',
        '/home/cril/wattez/XCSP17/QRandom/QRandom-bdd-18-21-2/bdd-18-21-2-133-78-06.xml.lzma',
        '/home/cril/wattez/XCSP17/CryptoPuzzle/CryptoPuzzle-m1-s1/CryptoPuzzle-no-no-yes.xml.lzma',
    ]

    STAT_TABLE_RESULT_SUB_INPUT_SET = {
        "CHS": {
            "count": 5,
            "sum": 130,
         'total': 5,
            "common count": 5,
            "common sum": 130,
            "uncommon count": 0
        },
        "ExplorationLuby": {
            "count": 5,
            "sum": 23,
         'total': 5,
            "common count": 5,
            "common sum": 23,
            "uncommon count": 0
        },
        "WDegCAxCD": {
            "count": 5,
            "sum": 47,
         'total': 5,
            "common count": 5,
            "common sum": 47,
            "uncommon count": 0
        }
    }

    SUB_XP_WARE_SET = [
        'CHS',
        'ExplorationLuby'
    ]

    STAT_TABLE_RESULT_SUB_XP_WARE_SET = {
        "CHS": {
            "count": 380,
            "sum": 59037,
         'total': 500,
            "common count": 380,
            "common sum": 26637,
            "uncommon count": 0
        },
        "ExplorationLuby": {
            "count": 389,
            "sum": 31402,
         'total': 500,
            "common count": 380,
            "common sum": 25761,
            "uncommon count": 9
        }
    }

    def setUp(self) -> None:
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, '../../data/xcsp17.json')
        jr = JsonReader(filename)
        self.campaign = jr.campaign

    def test_stat_table_no_vbs(self):
        analysis = Analysis(campaign=self.campaign)
        self.assertEqual(self.STAT_TABLE_RESULT_NO_VBS, analysis.get_stat_table().T.to_dict())
        self.assertEqual([45802, 103638, 105837], list(analysis.get_stat_table(par=[2, 10])['sumPAR2']))

    def test_stat_table_vbs(self):
        analysis = Analysis(campaign=self.campaign).add_vbew(['CHS', 'WDegCAxCD'], 'cpu_time')
        self.assertEqual(self.STAT_TABLE_RESULT_VBS, analysis.get_stat_table().T.to_dict())

    def test_stat_table_sub_set_inputs(self):
        analysis = Analysis(campaign=self.campaign).sub_analysis('input', self.SUB_INPUT_SET)
        self.assertEqual(self.STAT_TABLE_RESULT_SUB_INPUT_SET, analysis.get_stat_table().T.to_dict())

    def test_stat_table_sub_set_xpware(self):
        analysis = Analysis(campaign=self.campaign).sub_analysis('experiment_ware', self.SUB_XP_WARE_SET)
        self.assertEqual(analysis.get_stat_table().T.to_dict(), self.STAT_TABLE_RESULT_SUB_XP_WARE_SET)

    def test_contribution_table(self):
        cdfb = CampaignDataFrameBuilder(self.campaign).build_from_campaign()
        cdfb.data_frame['success'] = cdfb.data_frame.apply((lambda x: x['cpu_time'] < self.campaign.timeout), axis=1)
        contrib = ContributionTable(cdfb, [0, 10, 100])
        self.assertEqual('WDegCAxCD', contrib.get_figure().iloc[0].name)
        self.assertEqual(168, contrib.get_figure().iloc[0]['vbew 0s'])

    def test_error_table(self):
        self.campaign.experiments = self.campaign.experiments[600:]
        analysis = Analysis(campaign=self.campaign)
        self.assertEqual(600, analysis.get_error_table().n_errors.sum())
        self.assertTrue('600' in analysis.describe())

    def test_stat_table_common(self):
        self.campaign.experiments = self.campaign.experiments[200:]
        analysis = Analysis(campaign=self.campaign)
        self.assertTrue(len(set(analysis.get_stat_table()['common count'])) <= 1)

    def test_pivot_table_common(self):
        analysis = Analysis(campaign=self.campaign)
        self.assertEqual(500, len(analysis.get_pivot_table(pivot_val='cpu_time')))

    def test_description(self):
        analysis = Analysis(campaign=self.campaign)
        self.assertTrue('1500' in analysis.describe())


    def test_static_cactus_and_cdf(self):
        color_map = {
            'CHS': DEFAULT_COLORS[0],
            'WDegCAxCD': DEFAULT_COLORS[1],
            'ExplorationLuby': DEFAULT_COLORS[2],
            'vbew': DEFAULT_COLORS[3],
        }

        style_map = {
            'CHS': LINE_STYLES[0],
            'WDegCAxCD': LINE_STYLES[1],
            'ExplorationLuby': LINE_STYLES[2],
            'vbew': LINE_STYLES[3],
        }

        xp_ware_name_map = {
            'CHS': 'ChS',
            'WDegCAxCD': 'ca.cd',
            'ExplorationLuby': 'expLuby',
            'vbew': 'vbew',
        }

        analysis = Analysis(campaign=self.campaign).add_vbew({'CHS', 'WDegCAxCD'}, opti_col='cpu_time')
        analysis.get_cactus_plot(x_min=300, cumulated=True, color_map=color_map, style_map=style_map, xp_ware_name_map=xp_ware_name_map)
        plt.show()

        analysis.get_cdf(color_map=color_map, style_map=style_map, xp_ware_name_map=xp_ware_name_map, y_min=0.7, y_max=0.8)
        plt.show()


    def test_box(self):
        analysis = Analysis(campaign=self.campaign)
        analysis.get_box_plot()
        plt.show()

    def test_scatter(self):
        analysis = Analysis(campaign=self.campaign)
        analysis.get_scatter_plot(xp_ware_x='CHS', xp_ware_y='WDegCAxCD')
        plt.show()


if __name__ == '__main__':
    unittest.main()
