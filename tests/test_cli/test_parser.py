import unittest

from metrics.studio.cli.parser import parse_args


class ParserTestCase(unittest.TestCase):

    def test_json_case_without_plot_config(self):
        args = parse_args(["-i", "./data/xcsp17.json", "--from-json"])
        print(args)
        self.assertIsNotNone(args.input)
        self.assertTrue(args.from_json)
        self.assertTrue(args.from_yaml)

    def test_json_case_with_plot_config(self):
        args = parse_args(
            ["-i", "../data/xcsp17.json", "-p", "./data/config/plot/cactus-example.yml", "--from-json"])
        self.assertIsNotNone(args.input)
        with args.plot_config as plot_config:
            self.assertIsNotNone(plot_config)
        self.assertTrue(args.from_json)
        self.assertTrue(args.from_yaml)

    def test_yaml_case(self):
        args = parse_args(
            ["-i", "./data/config/parser/parser-config.yml", "--from-yaml"])
        self.assertIsNotNone(args.input)
        self.assertFalse(args.from_yaml)
        self.assertFalse(args.from_json)

    def test_failed_yaml_case(self):
        with self.assertRaises(SystemExit) as pytest_wrapped_e:
            args = parse_args(
                ["--from-yaml"])
            args.input.close()
        self.assertTrue(pytest_wrapped_e.exception.code == 2)
