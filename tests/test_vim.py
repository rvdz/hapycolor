from hapycolor import exceptions
from hapycolor import helpers
from hapycolor import palette
from hapycolor.targets.vim import Vim, VimColorManager
from tests.helpers import generate_palette, configurationtesting
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
        VimHelpers.pathogen_plugins_path()
    except:
        entries = [invalid_entry] * fails + [valid_entry]

    pathogen_mock = pathlib.Path(valid_entry)
    pathogen_finder = 'hapycolor.targets.vim_helpers.VimHelpers.pathogen_plugins_path'

    with mock.patch('builtins.input', side_effect=entries):
        with mock.patch(pathogen_finder, return_value=pathogen_mock):
            yield
    if pathlib.Path("./tests/hapycolor").exists():
        shutil.rmtree("./tests/hapycolor")


class TestVim(unittest.TestCase):
    @vimtesting()
    @configurationtesting()
    def test_vim_export_invalid_palette(self):
        """
        Asserting that vim's export functions works with an invalid palette
        """
        with self.assertRaises(exceptions.PaletteFormatError):
            Vim.export([], "vim_test")

    @vimtesting()
    @configurationtesting()
    def test_vim_export_0_color_palette(self):
        """
        Asserting that vim's export functions works with an empty palette
        """
        with self.assertRaises(exceptions.ColorFormatError):
            Vim.export(generate_palette(0), "vim_test")

    @vimtesting()
    @configurationtesting()
    def test_vim_export_1_color_palette(self):
        """ Asserting that vim's export functions works with a palette containing
            only one color """
        try:
            Vim.initialize_config()
            self.assertTrue(Vim.is_config_initialized())
            Vim.export(generate_palette(1), "vim_test")
        except Exception as err:
            self.fail(str(err))

    @vimtesting()
    @configurationtesting()
    def test_vim_export_16_color_palette(self):
        """
        Asserting that vim's export functions works with a 16 color palette
        """
        try:
            Vim.initialize_config()
            self.assertTrue(Vim.is_config_initialized())
            Vim.export(generate_palette(16), "vim_test")
        except Exception as err:
            self.fail(str(err))

    @vimtesting()
    @configurationtesting()
    def test_vim_export_200_color_palette(self):
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
        hsl_colors = ([(16  , 0.54 , 0.45) , (28  , 0.77 , 0.64) , (45  , 0.94 , 0.66) , (52  , 0.38 , 0.53) , (59  , 0.97 , 0.67) , (98  , 0.82 , 0.69) , (147 , 0.70 , 0.48) , (162 , 0.60 , 0.42) , (172 , 0.85 , 0.54) , (177 , 0.64 , 0.39) , (182 , 0.78 , 0.50) , (202 , 0.57 , 0.57) , (227 , 0.05 , 0.65) , (239 , 0.44 , 0.50) , (305 , 0.70 , 0.50) , (319 , 0.32 , 0.50) , (333 , 0.57 , 0.42) , (338 , 0.57 , 0.60) , (342 , 0.57 , 0.44) , (344 , 0.60 , 0.5)  , (348 , 0.92 , 0.62)])
        pltte.colors = [helpers.hsl_to_rgb(c) for c in hsl_colors]

        try:
            Vim.initialize_config()
            self.assertTrue(Vim.is_config_initialized())
            Vim.export(pltte, "vim_test")
        except Exception as e:
            self.fail(str(e))

    def test_vim_color_manager(self):
        """
        Tests the correct labelization of the colors and retrives them sorted
        according to the appropriate color manager's logic.
        """
        # Source of the rgb colors, took one color for each label
        # hsl_colors = [(25, 0.86, 0.53), (350, 0.762, 0.508), (86, 0.259, 0.57), (140, 0.450, 0.59), (256, 0.337, 0.511),  (175, 0.841, 0.511), (201, 0.708, 0.514), (112, 0.969, 0.50), (50, 0.458, 0.53), (230, 0.371, 0.533), (288, 0.443, 0.557), (320, 0.820, 0.527)]

        colors = [(238, 118, 32), (225, 34, 66), (149, 174, 117), (103, 197, 135), (111, 88, 172), (25, 235, 218), (43, 157, 219), (37, 251, 4), (190, 172, 80), (92, 106, 180), (172, 92, 192), (233, 35, 167)]
        expected_sorted_colors = [(238, 118, 32), (190, 172, 80), (149, 174, 117), (37, 251, 4), (103, 197, 134), (25, 235, 218), (43, 157, 219), (92, 107, 180), (110, 88, 172), (172, 92, 192), (233, 35, 167), (225, 34, 66), (238, 118, 32), (190, 172, 80), (149, 174, 117), (37, 251, 4), (103, 197, 134), (25, 235, 218), (43, 157, 219), (92, 107, 180), (110, 88, 172), (172, 92, 192), (233, 35, 167), (225, 34, 66)]

        vcm = VimColorManager(colors)
        sorted_colors = []
        for i in range(len(colors) * 2):
            sorted_colors.append(vcm.get_next_color())
        self.assertEqual(sorted_colors, expected_sorted_colors)
