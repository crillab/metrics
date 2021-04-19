import unittest

from metrics.wallet import Analysis


class AnalysisTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        inconsistent_returns = {'ERR WRONGCERT', 'ERR UNSAT'}
        successful_returns = {'SAT', 'UNSAT'}

        cls.analysis = Analysis(
            input_file='data/xcsp19/full_analysis/config/metrics_scalpel_full_paths.yml',
            is_consistent_by_xp=lambda x: not x['Checked answer'] in inconsistent_returns,
            is_consistent_by_input=lambda df: len(set(df['Checked answer'].unique()) & successful_returns) < 2,
            is_success=lambda x: x['Checked answer'] in successful_returns
        )

    def test_building(self):
        self.analysis.data_frame


if __name__ == '__main__':
    unittest.main()
