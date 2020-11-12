import os
from unittest import TestCase

from metrics.scalpel import CampaignParserListener, read_configuration


class TestReadConfiguration(TestCase):
    def setUp(self) -> None:
        self._example_dir = 'example/'

    def test_sat_competition(self) -> None:
        parser_listener = CampaignParserListener()
        configuration = read_configuration(os.path.join(self._example_dir, 'sat-competition/input/config.yml'),
                                           parser_listener)

        self.assertEqual(',', configuration.get_csv_configuration().get_separator())
        self.assertIsNone(configuration.get_csv_configuration().get_quote_char())
        self.assertTrue(configuration.get_csv_configuration().has_header())

    def test_multi_csv_with_custom_separator_and_no_header(self) -> None:
        parser_listener = CampaignParserListener()
        configuration = read_configuration(
            os.path.join(self._example_dir, 'multi-csv-with-custom-separator-and-no-header/input/config.yml'),
            parser_listener)

        self.assertEqual(' ', configuration.get_csv_configuration().get_separator())
        self.assertIsNone(configuration.get_csv_configuration().get_quote_char())

    def test_flat_dir(self) -> None:
        parser_listener = CampaignParserListener()
        configuration = read_configuration(
            os.path.join(self._example_dir, 'flat-dir/input/config.yml'),
            parser_listener)
        file_name_meta = configuration.get_file_name_meta()
        groups = {k: v for k, v in file_name_meta.get_groups()}
        self.assertEqual(2, len(groups))
        self.assertEqual(2, groups.get('experiment_ware'))
        self.assertEqual(1, groups.get('input'))
        self.assertEqual('ProblemFile-(.*)_(bs[012]{1})_(.*)', file_name_meta.get_regex_pattern())
