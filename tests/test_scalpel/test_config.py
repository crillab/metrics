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
        self.assertIsNone(configuration.get_experiment_ware_depth())
        self.assertEqual(1, configuration.get_hierarchy_depth())

    def test_multi_csv_with_custom_separator_and_no_header(self) -> None:
        parser_listener = CampaignParserListener()
        configuration = read_configuration(
            os.path.join(self._example_dir, 'multi-csv-with-custom-separator-and-no-header/input/config.yml'),
            parser_listener)

        self.assertEqual(' ', configuration.get_csv_configuration().get_separator())
        self.assertIsNone(configuration.get_csv_configuration().get_quote_char())
        self.assertFalse(configuration.get_csv_configuration().has_header())
        self.assertIsNone(configuration.get_experiment_ware_depth())
        self.assertEqual(1, configuration.get_hierarchy_depth())

    def test_flat_dir(self) -> None:
        parser_listener = CampaignParserListener()
        configuration = read_configuration(
            os.path.join(self._example_dir, 'flat-dir/input/config.yml'),
            parser_listener)
        file_name_meta = configuration.get_file_name_meta()
        self.assertEqual(2, file_name_meta.get_experiment_ware_group())
        self.assertEqual(1, file_name_meta.get_input_group())
        self.assertEqual('ProblemFile-(.*)_(bs[012]{1})_(.*)', file_name_meta.get_regex_pattern())
