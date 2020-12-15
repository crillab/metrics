import os
from unittest import TestCase

from metrics.wallet import Analysis


class TestReadConfigurationBug(TestCase):
    def setUp(self) -> None:
        self._example_dir = 'example/'

    def test_bug_gitlab_38(self):
        analysis = Analysis(
            input_file=os.path.join(self._example_dir, 'issue38/campaign/config/metrics_scalpel.yml'))
        columns = analysis.campaign_df.data_frame.columns
        self.assertTrue('best_bound' in columns)
        self.assertTrue('status' in columns)
