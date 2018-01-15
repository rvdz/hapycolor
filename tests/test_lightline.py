from hapycolor import exceptions
from hapycolor.targets.lightline import Lightline
from tests.helpers import disableprints
from unittest.mock import patch
import os
import pathlib
import shutil
import unittest


class TestLightline(unittest.TestCase):
    @disableprints()
    @patch('builtins.input', return_value="0")
    def test_theme_selection_valid(self, mock_input):
        self.assertIsInstance(Lightline.select_theme(), Lightline.ThemeEnum)

    @disableprints()
    @patch('builtins.input', side_effect=["999", "0"])
    def test_theme_selection_invalid_entry(self, mock_input):
        self.assertIsInstance(Lightline.select_theme(), Lightline.ThemeEnum)

    @disableprints()
    @patch('builtins.input', side_effect=["-1", "0"])
    def test_theme_selection_negative_entry(self, mock_input):
        self.assertIsInstance(Lightline.select_theme(), Lightline.ThemeEnum)

    @disableprints()
    @patch('builtins.input', side_effect=["-1", "999", "0"])
    def test_theme_selection_valid_third_attempt(self, mock_input):
        self.assertIsInstance(Lightline.select_theme(), Lightline.ThemeEnum)

    @patch('builtins.input', return_value="./tests/lightline.vim")
    def test_config_colorscheme_file_valid(self, mock_input):
        valid_colorscheme = "./tests/lightline.vim/autoload/lightline/colorscheme"
        os.makedirs(valid_colorscheme)
        p = Lightline.select_colorscheme_path()
        self.assertIsNotNone(p)
        shutil.rmtree("./tests/lightline.vim")

    @patch('builtins.input', return_value="./tests/lightline.vim")
    def test_config_colorscheme_file_invalid(self, mock_input):
        with self.assertRaises(exceptions.WrongInputError):
            Lightline.select_colorscheme_path()

    def test_theme_exist(self):
        for t in Lightline.ThemeEnum:
            self.assertTrue(pathlib.Path(t.value).exists())
