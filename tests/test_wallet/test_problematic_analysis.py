import unittest

from metrics.core.constants import ERROR_COL
from metrics.wallet import *


class ProblematicAnalysisTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        inconsistent_returns = {'ERR WRONGCERT', 'ERR UNSAT'}
        successful_returns = {'SAT', 'UNSAT'}

        cls.analysis = DecisionAnalysis(
            input_file='data/xcsp19/problematic_analysis/config/metrics_scalpel_full_paths.yml'
        )

        cls.analysis.check_success(lambda x: x['Checked answer'] in successful_returns)

        cls.analysis.check_input_consistency(
            lambda df: len(set(df['Checked answer'].unique()) & successful_returns) < 2)
        cls.analysis.check_xp_consistency(lambda x: not x['Checked answer'] in inconsistent_returns)

    def test_building(self):
        self.assertEqual(30, self.analysis.data_frame[ERROR_COL].sum())
        self.assertEqual(1, self.analysis.description_table().loc['n_missing_xp', 'analysis'])
        self.assertEqual(4, self.analysis.description_table().loc['n_inconsistent_xp', 'analysis'])
        self.assertEqual(26, self.analysis.description_table().loc['n_inconsistent_xp_due_to_input', 'analysis'])


if __name__ == '__main__':
    unittest.main()
