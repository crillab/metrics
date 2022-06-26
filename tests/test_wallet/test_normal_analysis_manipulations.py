import re
import os
import unittest

from metrics.core.constants import *
from metrics.wallet import find_best_cpu_time_input, import_analysis_from_file, DecisionAnalysis


class NormalAnalysisManipulationTestCase(unittest.TestCase):

    def setUp(self) -> None:
        inconsistent_returns = {'ERR WRONGCERT', 'ERR UNSAT'}
        successful_returns = {'SAT', 'UNSAT'}
        dirname = os.path.dirname(__file__)
        self._example_dir = os.path.join(dirname, '..', 'data')

        self.analysis = DecisionAnalysis(
            input_file=f'{self._example_dir}/xcsp19/full_analysis/config/metrics_scalpel_full_paths.yml'
        )

        self.analysis.check_input_consistency(
            lambda df: len(set(df['Checked answer'].unique()) & successful_returns) < 2)
        self.analysis.check_xp_consistency(lambda x: not x['Checked answer'] in inconsistent_returns)


    def test_builded_analysis(self):
        self.assertEqual(15600, len(self.analysis.data_frame))

    def test_errors(self):
        self.assertEqual(2131, len(self.analysis.error_table()))

    def test_filter_method(self):
        self.analysis = self.analysis.filter_analysis(lambda x: 'parallel' not in x['experiment_ware'])
        self.analysis = self.analysis.filter_analysis(lambda x: 'Many' not in x['experiment_ware'])

        self.assertEqual(9600, len(self.analysis.data_frame))

    def test_remove_experiment_wares(self):
        self.analysis = self.analysis.remove_experiment_wares({
            'Concrete 3.12.2',
            'cosoco 2.0'
        })

        self.assertEqual(13200, len(self.analysis.data_frame))

    def test_filter_method_2(self):
        self.analysis = self.analysis.filter_analysis(lambda x: 'CSP' == x['Category'])

        self.assertEqual(7800, len(self.analysis.data_frame))

    def test_mega_filtering(self):
        self.analysis = self.analysis.filter_analysis(lambda x: 'parallel' not in x['experiment_ware'])
        self.analysis = self.analysis.filter_analysis(lambda x: 'Many' not in x['experiment_ware'])
        self.analysis = self.analysis.remove_experiment_wares({
            'Concrete 3.12.2',
            'cosoco 2.0'
        })
        self.analysis = self.analysis.filter_analysis(lambda x: 'CSP' == x['Category'])

        self.assertEqual(3600, len(self.analysis.data_frame))

    def test_error_table(self):
        self.assertEqual(2131, len(self.analysis.error_table()))

    def test_new_variable(self):
        family_re = re.compile(r'^XCSP\d\d/(.*?)/')

        analysis = self.analysis.add_variable(
            new_var='family',
            function=lambda x: family_re.match(x['input']).group(1)
        )

        self.assertEqual(78, len(analysis.data_frame.family.unique()))

    def test_remove_variables(self):
        self.assertEqual(['input', 'experiment_ware', 'cpu_time', 'Category', 'Checked answer',
                          'Objective function', 'Wallclock time', 'Memory', 'Solver name',
                          'Solver version', 'timeout', 'success', 'user_success', 'missing',
                          'consistent_xp', 'consistent_input', 'error'], list(self.analysis.data_frame.columns))

        self.analysis = self.analysis.remove_variables(
            vars=['Category', 'Objective function']
        )

        self.assertEqual(['input', 'experiment_ware', 'cpu_time', 'Checked answer',
                          'Wallclock time', 'Memory', 'Solver name', 'Solver version', 'timeout',
                          'success', 'user_success', 'missing', 'consistent_xp',
                          'consistent_input', 'error'], list(self.analysis.data_frame.columns))

    def test_vbs(self):
        self.analysis = self.analysis.remove_experiment_wares({
            'Concrete 3.12.2',
            'cosoco 2.0'
        })

        self.assertEqual(600, len(self.analysis.inputs))

        self.analysis = self.analysis.add_virtual_experiment_ware(
            function=find_best_cpu_time_input,
            xp_ware_set=None,
            name='VBS'
        )

        self.assertEqual([600], list(self.analysis.data_frame.groupby(EXPERIMENT_XP_WARE).apply(lambda df: len(df)).unique()))
        self.assertEqual(600, len(self.analysis.inputs))

    def test_export(self):
        file = f'{self._example_dir}/xcsp19/full_analysis/analysis.csv'
        self.analysis.export(file)
        analysis = import_analysis_from_file(file)

        self.assertEqual(4509, self.analysis.data_frame[SUCCESS_COL].sum())
        self.assertEqual(4509, analysis.data_frame[SUCCESS_COL].sum())


if __name__ == '__main__':
    unittest.main()
