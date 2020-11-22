import json
import unittest

import jsonpickle

from metrics.core.builder.builder import CampaignBuilder
from metrics.core.constants import *
from metrics.core.model import Campaign


JSON_CAMPAIGN = {
    "name": "Une campagne de Napol\u00e9on",
    "timeout": 0.015,
    "memout": 0.015,
    "experiment_wares": [
        {
            "name": "MySolver",
            "id": 1,
            "date": "now",
            "checksum": "afhjlsdgjdgsf2q2d3",
            "last_modified": "now"
        }
    ],
    "input_set": {
        "name": "Ukulele bench",
        "inputs": [
            {
                "name": "/somewhere/over/the/rainbow/"
            },
            {
                "name": "/somewhere/under/the/rainbow/"
            }
        ]
    },
    "experiments": [
        {
            "input": "input",
            "experiment_ware": "ConAbs",
            "cpu_time": 1200.0,
            "id": 1,
            "start_time": "now"
        }
    ],
    "id": 1,
    "date": "now"
}


class CampaignTestCase(unittest.TestCase):

    def _create_input(self, builder, path):
        builder[INPUT_NAME] = path

    def _create_inputset(self, builder):
        builder[INPUT_SET_NAME] = 'Ukulele bench'
        self._create_input(builder.add_input_builder(), '/somewhere/over/the/rainbow/')
        self._create_input(builder.add_input_builder(), '/somewhere/under/the/rainbow/')

    def _create_experiment_ware(self, builder):
        builder['id'] = 1
        builder[XP_WARE_NAME] = 'MySolver'
        builder['date'] = 'now'
        builder['checksum'] = 'afhjlsdgjdgsf2q2d3'
        builder['last_modified'] = 'now'

    def _create_experiment_builder(self, builder):
        builder['id'] = 1
        builder[EXPERIMENT_INPUT] = 'input'
        builder['start_time'] = 'now'
        builder[EXPERIMENT_XP_WARE] = 'ConAbs'
        builder[EXPERIMENT_CPU_TIME] = 1200.

    def _create_campaign_builder(self):
        self.cb = CampaignBuilder()
        self.cb['id'] = 1
        self.cb[CAMPAIGN_NAME] = 'Une campagne de Napoléon'
        self.cb[CAMPAIGN_TIMEOUT] = 0.015
        self.cb[CAMPAIGN_MEMOUT] = 0.015
        self.cb['date'] = 'now'
        self._create_experiment_ware(self.cb.add_experiment_ware_builder())
        self._create_inputset(self.cb.add_input_set_builder())
        self._create_experiment_builder(self.cb.add_experiment_builder())

    def setUp(self) -> None:
        self._create_campaign_builder()

    def test_double_xp_ware_inside_builder(self):
        self.assertTrue((self.cb.has_experiment_ware_with_name('MySolver')))
        self.assertFalse((self.cb.has_experiment_ware_with_name('MySolvers')))

    def test_double_xp_ware_inside_builder_condition(self):
        with self.assertRaises(ValueError):
            self._create_experiment_ware(self.cb.add_experiment_ware_builder())

    def test_double_input_inside_builder(self):
        self.assertTrue((self.cb.has_input_with_name('/somewhere/over/the/rainbow/')))
        self.assertFalse((self.cb.has_input_with_name('/somewhere/over/the/rainbow/blue/birds/fly/')))

    def test_success_build_campaign(self):
        c = self.cb.build()
        self.assertTrue(isinstance(c, Campaign))

    def test_success_export_campaign(self):
        c = self.cb.build()
        json_c = jsonpickle.encode(c, unpicklable=False)
        self.assertEqual(JSON_CAMPAIGN, json.loads(json_c))

    def test_success_access_campaign_attr(self):
        c = self.cb.build()
        self.assertEqual(c.id, 1)

    def test_success_access_campaign_item(self):
        c = self.cb.build()
        self.assertEqual(c['id'], 1)

    def test_failed_build_campaign_type_error(self):
        with self.assertRaises(TypeError):
            self.cb['name'] = 1
            self.cb.build()

    def test_failed_build_campaign_key_error(self):
        self.cb._log_data['experiments']._elt = list()
        with self.assertRaises(TypeError):
            self.cb.build()

    def test_failed_build_campaign_list_type_error(self):
        with self.assertRaises(TypeError):
            self._create_experiment_ware('not an experiment ware')
            self.cb.build()


if __name__ == '__main__':
    unittest.main()
