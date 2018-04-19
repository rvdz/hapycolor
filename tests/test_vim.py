from hapycolor import exceptions
from hapycolor import helpers
from hapycolor import palette
from hapycolor.targets.vim import Vim, VimColorManager, environment
from tests.helpers import generate_palette, configurationtesting
import pathlib
from unittest import mock
import contextlib
import unittest


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
    @unittest.skip("Too long to compute")
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
                       (14, 0.7, 0.48), (16, 0.6, 0.42), (17, 0.8, 0.54),
                       (333, 0.57, 0.42), (338, 0.57, 0.60),
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

        groups = [
                  ["group1_1", "group1_2", "group1_3"],
                  ["group2"],
                  ["group3"],
                 ]

        expected = colors[:]
        vcm = VimColorManager(colors, 3)
        for i, minor_groups in enumerate(groups):
            result = []
            casted_colors = vcm.cast(i, len(minor_groups))
            for (group, color) in zip(minor_groups, casted_colors):
                result.append(color)
            color = result[-1]
            self.assertTrue(all([color == c for c in result]))
            self.assertIn(color, expected)

    @mock.patch('hapycolor.helpers.input_path',
           return_value=pathlib.Path("./README.md").expanduser())
    @mock.patch('hapycolor.targets.vim.environment.VimEnvironments.bundle_plugins_path',
           side_effect=exceptions.NoCommonPathFound(""))
    def test_file(self, mock_input, mock_bundle_path):
        """ Assert that 'save_vim' fails when a file is provided """
        with self.assertRaises(exceptions.WrongInputError):
            Vim.initialize_config()
