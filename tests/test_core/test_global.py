import os
import unittest

from tests.test_core.json_reader import JsonReader
from metrics.core.model import Campaign, InputSet


class MyTestCase(unittest.TestCase):

    def setUp(self) -> None:
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, '../../data/xcsp17.json')
        jr = JsonReader(filename)
        self.campaign = jr.campaign

    def test_equalities(self):
        self.assertIsInstance(self.campaign, Campaign)
        self.assertEqual(self.campaign.name, 'bandit of heuristics - xcsp17_csp')
        self.assertEqual(self.campaign.timeout, 3600)
        self.assertEqual(self.campaign.memout, 9999999999)
        self.assertIsInstance(self.campaign.experiment_wares, list)
        self.assertEqual(self.campaign.experiment_wares[0].name, 'CHS')
        self.assertEqual(self.campaign.experiment_wares[2].name, 'WDegCAxCD')
        self.assertIsInstance(self.campaign.experiments, list)
        self.assertEqual(self.campaign.experiments[0].input, '/home/cril/wattez/XCSP17/SuperSolutions/SuperSolutions-Taillard-os04/SuperTaillard-os-04-26.xml.lzma')
        self.assertEqual(self.campaign.experiments[-1].input, '/home/cril/wattez/XCSP17/Wwtpp/Wwtpp-ord-s1/Wwtpp-ord-ex08540.xml.lzma')
        self.assertIsInstance(self.campaign.input_set, InputSet)
        self.assertEqual(self.campaign.input_set.inputs[0].name, '/home/cril/wattez/XCSP17/SuperSolutions/SuperSolutions-Taillard-os04/SuperTaillard-os-04-26.xml.lzma')
        self.assertEqual(self.campaign.input_set.inputs[0].family, 'SuperSolutions')
        self.assertEqual(self.campaign.input_set.inputs[-1].name, '/home/cril/wattez/XCSP17/Wwtpp/Wwtpp-ord-s1/Wwtpp-ord-ex08540.xml.lzma')
        self.assertEqual(self.campaign.input_set.inputs[-1].family, 'Wwtpp')


if __name__ == '__main__':
    unittest.main()
