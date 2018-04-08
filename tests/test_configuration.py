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
    def test_context(lines=None):
        test_file = "./tests/test_configuration_editor.txt"
        text = """first line
second line
third line
fourth line
"""
        with open(test_file, 'w') as f:
            f.write(text)
            if lines:
                f.write(lines)

        with mock.patch("hapycolor.config.ConfigurationEditor.get_config_file",
                return_value=test_file):
            yield
        os.remove(test_file)

    @test_context()
    def test_replace_line_with_match(self):
        """
        This test aims at testing if the return of the match is correctly
        passed to the substitution function. In this case, the regex should
        capture the string 'line' in the second line, and replace the begging
        of the line by 'middle'.
        """
        pattern = r"^second (.*)$"
        config.ConfigurationEditor.replace_line(pattern,
                lambda m: "middle " + m.group(1))

        expected = "middle line\n"
        match = False
        with open(config.ConfigurationEditor.get_config_file(), 'r') as f:
            self.assertEqual(expected, f.readlines()[1])

    @test_context()
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

        config.ConfigurationEditor.replace_line(pattern, substitution,
                [[1, 2, 3, 4], 0])

        expected = ["Color 1\n", "Color 2\n", "Color 3\n", "Color 4\n"]
        match = False
        with open(config.ConfigurationEditor.get_config_file(), 'r') as f:
            for i, l in enumerate(f.readlines()):
                self.assertEqual(expected[i], l)
