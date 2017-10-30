from hapycolor import config
from hapycolor.export import vim, iterm, wallpaper
from shutil import copyfile
from hapycolor import exceptions
from hapycolor import palette
from hapycolor import helpers

from unittest.mock import patch

import contextlib
import pathlib
import unittest

def get_palette(size):
    pltte = palette.Palette()
    pltte.foreground = (0,0,0)
    pltte.background = (0,0,0)
    pltte.colors = [(c,c,c) for c in range(size)]
    return pltte

@contextlib.contextmanager
def vimtesting():
    import os
    mock_vim_path = config.ROOT_DIR + "/../tests/test_targets_vim.vim"
    with patch('hapycolor.config.vim', return_value=mock_vim_path):
        yield
    if pathlib.Path(mock_vim_path).exists():
        os.remove(mock_vim_path)

class TestVim(unittest.TestCase):
    @vimtesting()
    def test_vim_export_invalid_palette(self):
        """ Asserting that vim's export functions works with an empty palette """
        with self.assertRaises(exceptions.PaletteFormatError):
            vim.Vim.profile([], "vim_test", "wallpaper_path")

    @vimtesting()
    def test_vim_export_0_color_palette(self):
        """ Asserting that vim's export functions works with an empty palette """
        with self.assertRaises(exceptions.ColorFormatError):
            vim.Vim.profile(get_palette(0), "vim_test", "wallpaper_path")

    @vimtesting()
    def test_vim_export_1_color_palette(self):
        """ Asserting that vim's export functions works with a palette containing
            only one color """
        try:
            vim.Vim.profile(get_palette(1), "vim_test", "wallpaper_path")
        except Exception as err:
            self.fail(str(err))

    @vimtesting()
    def test_vim_export_16_color_palette(self):
        """ Asserting that vim's export functions works with a 16 color palette """
        try:
            vim.Vim.profile(get_palette(16), "vim_test", "wallpaper_path")
        except Exception as err:
            self.fail(str(err))

    @vimtesting()
    def test_vim_export_200_color_palette(self):
        """ Asserting that vim's export functions works with a 200 color palette """
        try:
            vim.Vim.profile(get_palette(200), "vim_test", "wallpaper_path")
        except Exception as err:
            self.fail(str(err))


    @vimtesting()
    def test_profile(self):
        """ Vim Integration test: provides a valid set of colors to the main function and check if it does not
            fail """
        pltte = palette.Palette()
        pltte.foreground = (0,0,0)
        pltte.background = (0,0,0)
        hsl_colors = ([(16  , 0.54 , 0.45) , (28  , 0.77 , 0.64) , (45  , 0.94 , 0.66) , (52  , 0.38 , 0.53) , (59  , 0.97 , 0.67) , (98  , 0.82 , 0.69) , (147 , 0.70 , 0.48) , (162 , 0.60 , 0.42) , (172 , 0.85 , 0.54) , (177 , 0.64 , 0.39) , (182 , 0.78 , 0.50) , (202 , 0.57 , 0.57) , (227 , 0.05 , 0.65) , (239 , 0.44 , 0.50) , (305 , 0.70 , 0.50) , (319 , 0.32 , 0.50) , (333 , 0.57 , 0.42) , (338 , 0.57 , 0.60) , (342 , 0.57 , 0.44) , (344 , 0.60 , 0.5)  , (348 , 0.92 , 0.62)])
        pltte.colors = [helpers.hsl_to_rgb(c) for c in hsl_colors]

        try:
            vim.Vim.profile(pltte, "vim_test", "wallpaper_path")
        except Exception as e:
            self.fail(str(e))
