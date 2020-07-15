import os
import unittest

import matplotlib.pyplot as plt

from tests.test_core.json_reader import JsonReader
from metrics.wallet.dataframe.builder import CampaignDataFrameBuilder
from metrics.wallet.figure.static_figure import StatTable, CactusMPL, BoxMPL, ScatterMPL, LINE_STYLES, \
    ContributionTable, DEFAULT_COLORS


class MyTestCase(unittest.TestCase):
    STAT_TABLE_RESULT_NO_VBS = {
        'CHS': {'common_count': 374,
                'common_sum': 21656,
                'count': 380,
                'sum': 66237,
                'total': 500,
                'uncommon_count': 6},
        'ExplorationLuby': {'common_count': 374,
                            'common_sum': 22161,
                            'count': 389,
                            'sum': 38602,
                            'total': 500,
                            'uncommon_count': 15},
        'WDegCAxCD': {'common_count': 374,
                      'common_sum': 27034,
                      'count': 381,
                      'sum': 67638,
                      'total': 500,
                      'uncommon_count': 7}}

    STAT_TABLE_RESULT_VBS = {
        "CHS": {
            "count": 380,
            "sum": 66237,
         'total': 500,
            "common_count": 374,
            "common_sum": 21656,
            "uncommon_count": 6
        },
        "ExplorationLuby": {
            "count": 389,
            "sum": 38602,
         'total': 500,
            "common_count": 374,
            "common_sum": 22161,
            "uncommon_count": 15
        },
        "WDegCAxCD": {
            "count": 381,
            "sum": 67638,
         'total': 500,
            "common_count": 374,
            "common_sum": 27034,
            "uncommon_count": 7
        },
        "vbew": {
            "count": 387,
            "sum": 39302,
         'total': 500,
            "common_count": 374,
            "common_sum": 15317,
            "uncommon_count": 13
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
            "common_count": 5,
            "common_sum": 130,
            "uncommon_count": 0
        },
        "ExplorationLuby": {
            "count": 5,
            "sum": 23,
         'total': 5,
            "common_count": 5,
            "common_sum": 23,
            "uncommon_count": 0
        },
        "WDegCAxCD": {
            "count": 5,
            "sum": 47,
         'total': 5,
            "common_count": 5,
            "common_sum": 47,
            "uncommon_count": 0
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
            "common_count": 380,
            "common_sum": 26637,
            "uncommon_count": 0
        },
        "ExplorationLuby": {
            "count": 389,
            "sum": 31402,
         'total': 500,
            "common_count": 380,
            "common_sum": 25761,
            "uncommon_count": 9
        }
    }

    def setUp(self) -> None:
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, '../../data/xcsp17.json')
        jr = JsonReader(filename)
        self.campaign = jr.campaign

    def test_stat_table_no_vbs(self):
        campaign_df = CampaignDataFrameBuilder(self.campaign).build_from_campaign()
        campaign_df.data_frame['success'] = campaign_df.data_frame.apply((lambda x: x['cpu_time'] < self.campaign.timeout), axis=1)
        stat = StatTable(campaign_df)
        self.assertEqual(self.STAT_TABLE_RESULT_NO_VBS, stat.get_figure().T.to_dict())

    def test_stat_table_vbs(self):
        cdfb = CampaignDataFrameBuilder(self.campaign).build_from_campaign().add_vbew(['CHS', 'WDegCAxCD'], 'cpu_time')
        cdfb.data_frame['success'] = cdfb.data_frame.apply((lambda x: x['cpu_time'] < self.campaign.timeout), axis=1)
        stat = StatTable(cdfb)
        self.assertEqual(self.STAT_TABLE_RESULT_VBS, stat.get_figure().T.to_dict())

    def test_stat_table_sub_set_inputs(self):
        cdfb = CampaignDataFrameBuilder(self.campaign).build_from_campaign().sub_data_frame('input', self.SUB_INPUT_SET)
        cdfb.data_frame['success'] = cdfb.data_frame.apply((lambda x: x['cpu_time'] < self.campaign.timeout), axis=1)
        stat = StatTable(cdfb)
        self.assertEqual(self.STAT_TABLE_RESULT_SUB_INPUT_SET,stat.get_figure().T.to_dict())

    def test_stat_table_sub_set_xpware(self):
        cdfb = CampaignDataFrameBuilder(self.campaign).build_from_campaign().sub_data_frame('experiment_ware', self.SUB_XP_WARE_SET)
        cdfb.data_frame['success'] = cdfb.data_frame.apply((lambda x: x['cpu_time'] < self.campaign.timeout), axis=1)
        stat = StatTable(cdfb)
        self.assertEqual(stat.get_figure().T.to_dict(), self.STAT_TABLE_RESULT_SUB_XP_WARE_SET)

    def test_contribution_table(self):
        cdfb = CampaignDataFrameBuilder(self.campaign).build_from_campaign()
        cdfb.data_frame['success'] = cdfb.data_frame.apply((lambda x: x['cpu_time'] < self.campaign.timeout), axis=1)
        contrib = ContributionTable(cdfb, [0, 10, 100])
        self.assertEqual('WDegCAxCD', contrib.get_figure().iloc[0].name)
        self.assertEqual(168, contrib.get_figure().iloc[0].vbew_simple)

    def test_static_cactus(self):
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

        cdfb = CampaignDataFrameBuilder(self.campaign).build_from_campaign()
        cdfb.data_frame['success'] = cdfb.data_frame.apply((lambda x: x['cpu_time'] < self.campaign.timeout), axis=1)
        cdfb = cdfb.add_vbew({'CHS', 'WDegCAxCD'}, opti_col='cpu_time')
        cactus = CactusMPL(cdfb, x_min=300, cumulated=True, color_map=color_map, style_map=style_map, xp_ware_name_map=xp_ware_name_map)
        cactus.get_figure()

        #plt.savefig('cactus.pdf', transparent=True, bbox_inches='tight', figsize=(7, 2))
        plt.show()

    def test_box(self):
        cdfb = CampaignDataFrameBuilder(self.campaign).build_from_campaign()
        cdfb.data_frame['success'] = cdfb.data_frame.apply((lambda x: x['cpu_time'] < self.campaign.timeout), axis=1)
        box = BoxMPL(cdfb)
        box.get_figure()
        plt.show()

    def test_scatter(self):
        cdfb = CampaignDataFrameBuilder(self.campaign).build_from_campaign()
        cdfb.data_frame['success'] = cdfb.data_frame.apply((lambda x: x['cpu_time'] < self.campaign.timeout), axis=1)
        scatter = ScatterMPL(cdfb, 'CHS', 'WDegCAxCD')
        scatter.get_figure()
        plt.show()


if __name__ == '__main__':
    unittest.main()
