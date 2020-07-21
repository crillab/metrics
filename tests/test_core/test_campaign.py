import unittest
from datetime import datetime

from metrics.core.builder.builder import CampaignBuilder, AttributeManagerSets
from metrics.core.model import Campaign


class CampaignTestCase(unittest.TestCase):

    def _create_input(self, builder, path):
        builder['path'] = path

    def _create_inputset(self, builder):
        builder['name'] = 'Ukulele bench'
        self._create_input(builder.add_input_builder(), '/somewhere/over/the/rainbow/')
        self._create_input(builder.add_input_builder(), '/somewhere/under/the/rainbow/')

    def _create_experiment_ware(self, builder):
        builder['id'] = 1
        builder['name'] = 'MySolver'
        builder['date'] = datetime.now()
        builder['checksum'] = 'afhjlsdgjdgsf2q2d3'
        builder['last_modified'] = datetime.now()

    def _create_experiment_builder(self, builder):
        builder['id'] = 1
        builder['input'] = 'input'
        builder['start_time'] = datetime.now()
        builder['experiment_ware'] = 'ConAbs'
        builder['cpu_time'] = 1200.

    def _create_campaign_builder(self):
        self.cb = CampaignBuilder()
        self.cb['id'] = 1
        self.cb['name'] = 'Une campagne de Napoléon'
        self.cb['timeout'] = 0.015
        self.cb['memout'] = 0.015
        self.cb['date'] = datetime.now()
        self._create_experiment_ware(self.cb.add_experiment_ware_builder())
        self._create_inputset(self.cb.add_input_set_builder())
        self._create_experiment_builder(self.cb.add_experiment_builder())

    def setUp(self) -> None:
        self._create_campaign_builder()

    def test_double_xp_ware_inside_builder(self):
        self.assertTrue((self.cb.is_experiment_ware_name_exist('MySolver')))
        self.assertFalse((self.cb.is_experiment_ware_name_exist('MySolvers')))

    def test_double_xp_ware_inside_builder_condition(self):
        with self.assertRaises(ValueError):
            self._create_experiment_ware(self.cb.add_experiment_ware_builder())

    def test_double_input_inside_builder(self):
        self.assertTrue((self.cb.is_input_path_exist('/somewhere/over/the/rainbow/')))
        self.assertFalse((self.cb.is_input_path_exist('/somewhere/over/the/rainbow/blue/birds/fly/')))

    def test_success_build_campaign(self):
        c = self.cb.build()
        self.assertTrue(isinstance(c, Campaign))

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
