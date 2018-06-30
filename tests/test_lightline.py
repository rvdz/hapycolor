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

    def test_theme_exist(self):
        for t in Lightline.ThemeEnum:
            self.assertTrue(pathlib.Path(t.value).exists())

    @unittest.skipUnless(pathlib.Path("~/.vim/pack/bundle/start/lightline.vim")
        .expanduser().is_dir(), "This test requires vim's plugins to be "
        + "located in this folder: '~/vim/pack/bundle/start")
    def test_select_colorscheme_path(self):
        path = Lightline.select_colorscheme_path()
        expected = "~/.vim/pack/bundle/start/lightline.vim/autoload/lightline" \
                    + "/colorscheme/hapycolor.vim"
        self.assertEqual(path, pathlib.Path(expected).expanduser().as_posix())
