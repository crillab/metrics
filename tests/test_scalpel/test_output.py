import os
from unittest import TestCase

from metrics.wallet import BasicAnalysis


class TestReadConfigurationBug(TestCase):
    def setUp(self) -> None:
        dirname = os.path.dirname(__file__)
        self._example_dir = os.path.join(dirname, '..', 'data')

    def test_bug_gitlab_38(self):
        analysis = BasicAnalysis(
            input_file=os.path.join(self._example_dir, 'issue38/campaign/config/metrics_scalpel.yml'))
        columns = analysis.data_frame.columns
        self.assertTrue('best_bound' in columns)
        self.assertTrue('status' in columns)
