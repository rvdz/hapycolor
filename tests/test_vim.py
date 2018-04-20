from unittest import mock
import contextlib
import json
import pathlib
import unittest
from hapycolor import exceptions
from hapycolor import helpers
from hapycolor import palette
from hapycolor.targets.vim import Vim, ColorManager, environment
from tests.helpers import generate_palette, configurationtesting

@contextlib.contextmanager
def vimtesting(fails=0):
    import shutil
    import pathlib

    valid_entry = "./tests"
    invalid_entry = "./tests/run_suite.py"
    entries = []
    try:
        environment.VimEnvironments.bundle_plugins_path()
    except exceptions.NoCommonPathFound:
        entries = [invalid_entry] * fails + [valid_entry]

    bundle_mock = pathlib.Path(valid_entry)
    bundle_finder = 'hapycolor.targets.vim.environment.VimEnvironments.bundle_plugins_path'

    with mock.patch('builtins.input', side_effect=entries):
        with mock.patch(bundle_finder, return_value=bundle_mock):
            yield
    if pathlib.Path("./tests/hapycolor").exists():
        shutil.rmtree("./tests/hapycolor")


class TestVim(unittest.TestCase):
    @vimtesting()
    @configurationtesting()
    def test_export_invalid_palette(self):
        """
        Asserting that vim's export functions works with an invalid palette
        """
        with self.assertRaises(exceptions.PaletteFormatError):
            Vim.export([], "vim_test")

    @vimtesting()
    @configurationtesting()
    def test_export_0_color_palette(self):
        """
        Asserting that vim's export functions works with an empty palette
        """
        with self.assertRaises(exceptions.ColorFormatError):
            Vim.export(generate_palette(0), "vim_test")

    @vimtesting()
    @configurationtesting()
    def test_export_8_color_palette(self):
        """
        Asserting that vim's export functions works with a 16 color palette
        """
        try:
            Vim.initialize_config()
            self.assertTrue(Vim.is_config_initialized())
            Vim.export(generate_palette(8), "vim_test")
        except Exception as err:
            self.fail(str(err))

    @vimtesting()
    @configurationtesting()
    @unittest.skip("Too long to compute")
    def test_export_200_color_palette(self):
        """
        Asserting that vim's export functions works with a 200 color palette
        """
        try:
            Vim.initialize_config()
            self.assertTrue(Vim.is_config_initialized())
            Vim.export(generate_palette(200), "vim_test")
        except Exception as err:
            self.fail(str(err))

    @vimtesting()
    @configurationtesting()
    def test_export(self):
        """
        Vim Integration test: provides a valid set of colors to the main
        function and check if it does not fail
        """
        pltte = palette.Palette()
        pltte.foreground = (0, 0, 0)
        pltte.background = (0, 0, 0)
        hsl_colors = ([(16, 0.5, 0.45), (2, 0.7, 0.64), (4, 0.9, 0.66),
                       (5, 0.3, 0.53), (5, 0.9, 0.67), (9, 0.8, 0.69),
                       (342, 0.57, 0.44), (344, 0.60, 0.5),
                       (348, 0.92, 0.62)])
        pltte.colors = [helpers.hsl_to_rgb(c) for c in hsl_colors]

        try:
            Vim.initialize_config()
            self.assertTrue(Vim.is_config_initialized())
            Vim.export(pltte, "vim_test")
        except Exception as e:
            self.fail(str(e))


    def test_color_manager(self):
        """
        Tests the correct labelization of the colors and retrives them sorted
        according to the appropriate color manager's logic.
        """
        colors = [(12, 34, 56), (23, 45, 67), (150, 150, 150)]

        mock_frequencies = {'group_1_1': 101, 'group_2': 100, 'group_3': 1}
        mock_groups = {
                       "group_1_1": ["group_1_1", "group_1_2", "group_1_3"],
                       "group_2": ["group_2"],
                       "group_3": ["group_3"],
                      }

        expected = colors[:]
        with mock.patch("hapycolor.targets.vim.Vim.groups", mock_groups), \
                mock.patch("hapycolor.targets.vim.ColorManager.load_frequencies",
                        return_value=mock_frequencies):
            color_manager = ColorManager(colors)
            for minor_group in mock_groups:
                result = []
                casted_colors = color_manager.cast(minor_group)

                if minor_group == "group_1_1":
                    occurrences = 3
                    self.assertEqual(len(casted_colors), 3)
                else:
                    occurrences = 1
                    self.assertEqual(len(casted_colors), 1)
                self.assertEqual([casted_colors[0]] * occurrences, casted_colors)

    def test_color_manager_correct_frequencies_cast(self):
        colors = [(150, 10, 10), (160, 10, 10), (10, 10, 200), (20, 20, 200),
                  (10, 255, 10)]
        mock_frequencies = {
                            'group_1': 5,
                            'group_2': 100,
                            'group_3': 4,
                            'group_4': 3,
                            'group_5': 101,
                           }
        mock_groups = {
                       "group_1": ["group_1"],
                       "group_2": ["group_2"],
                       "group_3": ["group_3"],
                       "group_4": ["group_4"],
                       "group_5": ["group_5"],
                      }

        expected = colors[:]
        groups_colors = {}
        with mock.patch("hapycolor.targets.vim.Vim.groups", mock_groups), \
                mock.patch("hapycolor.targets.vim.ColorManager.load_frequencies",
                        return_value=mock_frequencies):
            color_manager = ColorManager(colors)
            for minor_group in mock_groups:
                groups_colors[minor_group] = color_manager.cast(minor_group)

        not_expected = [(150, 10, 10), (160, 10, 10)]
        result = [groups_colors["group_5"], groups_colors["group_2"]]
        self.assertNotEqual(result, not_expected)
        not_expected = [(160, 10, 10), (150, 10, 10)]
        self.assertNotEqual(result, not_expected)


    @unittest.skip("TODO(yann): Still not supported")
    def test_color_manager_duplicate_frequency(self, mock_frequencies):
        colors = [(150, 10, 10), (160, 10, 10), (10, 10, 200)]
        mock_frequencies = { 'group_1': 5, 'group_2': 100, 'group_3': 5 }
        mock_groups = {
                       "group_1": ["group_1"],
                       "group_2": ["group_2"],
                       "group_3": ["group_3"],
                      }
        with mock.patch("hapycolor.targets.vim.Vim.groups", mock_groups), \
                mock.patch("hapycolor.targets.vim.ColorManager.load_frequencies",
                        return_value=mock_frequencies):
            try:
                color_manager = ColorManager(colors)
            except Exception as e:
                self.fail(str(e))

    @mock.patch('hapycolor.helpers.input_path',
           return_value=pathlib.Path("./README.md").expanduser())
    @mock.patch('hapycolor.targets.vim.environment.VimEnvironments.bundle_plugins_path',
           side_effect=exceptions.NoCommonPathFound(""))
    def test_file(self, mock_input, mock_bundle_path):
        """ Assert that 'save_vim' fails when a file is provided """
        with self.assertRaises(exceptions.WrongInputError):
            Vim.initialize_config()
