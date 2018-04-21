from hapycolor import config
import os
import contextlib
import unittest
from unittest import mock


class TestConfiguration(unittest.TestCase):
    def test_config_sections(self):
        """ Assert that the correct sections exist in the config file """
        import configparser

        configuration = configparser.ConfigParser()
        configuration.read(config.get_default_config())
        expected_sections = ["hyperplan", "Iterm", "Wallpaper", "Gnome"]
        self.assertEqual(set(expected_sections), set(configuration.sections()))


    @contextlib.contextmanager
    def test_context(output):
        @contextlib.contextmanager
        def mock_edit_config(file):
            text = ["first line", "second line", "third line", "fourth line"]
            yield text, output

        with mock.patch("hapycolor.config.ConfigurationEditor.edit_config",
                        mock_edit_config):
            yield

    def test_replace_line_with_match(self):
        """
        This test aims at testing if the return of the match is correctly
        passed to the substitution function. In this case, the regex should
        capture the string 'line' in the second line, and replace the begging
        of the line by 'middle'.
        """
        result = []
        pattern = r"^second (.*)$"
        with TestConfiguration.test_context(result):
            match = config.ConfigurationEditor.replace_line("", pattern,
                    lambda m: "middle " + m.group(1))

        expected = "middle line"
        self.assertTrue(match)
        self.assertEqual(expected, result[1])

    def test_replace_line_with_argument(self):
        """
        This test aims at checking if the substitution arguments are passed
        correctly. It will try to replace each line where the string'line' is
        matched and replace it with 'Color %i', for i in range(1, 4). The
        substitution function, when called, will retrieve an element at index
        'index' of the list, and then increment the latter variable, so that,
        when the function will be called again, the next color will be
        returned.
        """
        pattern = r"^.*line$"
        def substitution(m, args):
            colors = args[0]
            index = args[1]
            res = "Color {}".format(colors[index])
            args[1] = (args[1] + 1) % len(args[0])
            return res

        result = []
        with TestConfiguration.test_context(result):
            config.ConfigurationEditor.replace_line("", pattern, substitution,
                    [[1, 2, 3, 4], 0])

        expected = ["Color 1", "Color 2", "Color 3", "Color 4"]
        match = False
        self.assertEqual(expected, result)
