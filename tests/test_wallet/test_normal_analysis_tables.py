import re
import unittest

from metrics.core.constants import *
from metrics.wallet import Analysis, find_best_cpu_time_input, import_analysis_from_file


class NormalAnalysisTablesTestCase(unittest.TestCase):

    def setUp(self) -> None:
        inconsistent_returns = {'ERR WRONGCERT', 'ERR UNSAT'}
        successful_returns = {'SAT', 'UNSAT'}

        self.analysis = Analysis(
            input_file='data/xcsp19/full_analysis/config/metrics_scalpel_full_paths.yml'
        )

        self.analysis.check_input_consistency(
            lambda df: len(set(df['Checked answer'].unique()) & successful_returns) < 2)
        self.analysis.check_xp_consistency(lambda x: not x['Checked answer'] in inconsistent_returns)

    def test_analysis_description(self):
        df = self.analysis.description_table()

        self.assertEqual(24, df.loc['n_experiment_wares', 'analysis'])
        self.assertEqual(600, df.loc['n_inputs', 'analysis'])
        self.assertEqual(15600, df.loc['n_experiments', 'analysis'])
        self.assertEqual(2100, df.loc['n_missing_xp', 'analysis'])
        self.assertEqual(31, df.loc['n_inconsistent_xp', 'analysis'])
        self.assertEqual(0, df.loc['n_inconsistent_xp_due_to_input', 'analysis'])

    def test_stat_table(self):
        df = self.analysis.stat_table()

        self.assertEqual(291, df.loc['Concrete 3.12.2', 'count'])
        self.assertEqual(255, df.loc['cosoco 2.0', 'count'])
        self.assertEqual(2353, df.loc['AbsCon 2019-07-23', 'common sum'])

    def test_pivot_table(self):
        self.analysis = self.analysis.remove_experiment_wares({
            'Concrete 3.12.2',
            'cosoco 2.0'
        })

        df = self.analysis.pivot_table(
            index='input',
            columns='experiment_ware',
            values='cpu_time',
        )

        self.assertEqual(3.65329, df.loc['XCSP17/AllInterval/AllInterval-m1-s1/AllInterval-035.xml', 'AbsCon 2019-07-23'])

    def test_contribution_table(self):
        df = self.analysis.contribution_table()

        #print(df)

        self.assertEqual(67, df.loc['PicatSAT 2019-09-12', 'vbew simple'])
        self.assertEqual(3, df.loc['PicatSAT 2019-09-12', 'contribution'])


if __name__ == '__main__':
    unittest.main()
