from hapycolor import config
from hapycolor import exceptions
from hapycolor import palette
from hapycolor import helpers
from hapycolor.export.iterm import Iterm, TermColorManager, TermColorEnum
from shutil import copyfile
from unittest.mock import patch

import contextlib
import unittest

def get_palette(size):
    pltte = palette.Palette()
    pltte.foreground = (0,0,0)
    pltte.background = (0,0,0)
    pltte.colors = [(c,c,c) for c in range(size)]
    return pltte


@contextlib.contextmanager
def itermtesting():
    import os
    test_config_path= config.ROOT_DIR + "/../tests/com.googlecode.iterm2.plist"
    tmp_test_config_path= config.ROOT_DIR + "/../tests/com.googlecode.iterm2.tmp"
    copyfile(test_config_path, tmp_test_config_path)
    with patch('hapycolor.config.iterm_config', return_value=tmp_test_config_path):
        yield
    os.remove(tmp_test_config_path)

class TestIterm(unittest.TestCase):
    def test_valid_template(self):
        """ Checks that the template file is valid """
        import xml.etree.ElementTree as ET
        try:
            root = ET.parse(config.iterm_template())
        except ET.ParseError as err:
            self.fail(str(err))

    @itermtesting()
    def test_profile(self):
        """ iTerm Integration test: provides a valid set of colors to the main function and check if it does not
            fail """
        pltte = palette.Palette()
        pltte.foreground = (0,0,0)
        pltte.background = (0,0,0)
        hsl_colors =  ([(16  , 0.54 , 0.45) , (28  , 0.77 , 0.64) , (45  , 0.94 , 0.66) , (52  , 0.38 , 0.53) , (59  , 0.97 , 0.67) , (98  , 0.82 , 0.69) , (147 , 0.70 , 0.48) , (162 , 0.60 , 0.42) , (172 , 0.85 , 0.54) , (177 , 0.64 , 0.39) , (182 , 0.78 , 0.50) , (202 , 0.57 , 0.57) , (227 , 0.05 , 0.65) , (239 , 0.44 , 0.50) , (305 , 0.70 , 0.50) , (319 , 0.32 , 0.50) , (333 , 0.57 , 0.42) , (338 , 0.57 , 0.60) , (342 , 0.57 , 0.44) , (344 , 0.60 , 0.5)  , (348 , 0.92 , 0.62)])
        pltte.colors = [helpers.hsl_to_rgb(c) for c in hsl_colors]
        try:
            Iterm.profile(pltte, "iterm_test", "wallpaper_path")
        except Exception as e:
            self.fail(str(e))

    @itermtesting()
    def test_valid_basic_configuration(self):
        """ Checks that the basic configuration file is valid """
        import xml.etree.ElementTree as ET
        try:
            root = ET.parse(config.iterm_config())
        except ET.ParseError as err:
            self.fail(str(err))

    @itermtesting()
    def test_export_iterm_0_color_palette(self):
        with self.assertRaises(exceptions.ColorFormatError):
            Iterm.profile(get_palette(0), "iterm_test", "wallpaper_path")

    @itermtesting()
    @unittest.skip("Still needs to implement palette management for iterm")
    def test_export_iterm_1_color_palette(self):
        try:
            Iterm.profile(get_palette(1), "iterm_test", "wallpaper_path")
        except Exception as err:
            self.fail(str(err))

    @itermtesting()
    def test_export_iterm_16_color_palette(self):
        try:
            Iterm.profile(get_palette(16), "iterm_test", "wallpaper_path")
        except Exception as err:
            self.fail(str(err))

    @itermtesting()
    def test_export_iterm_200_color_palette(self):
        try:
            Iterm.profile(get_palette(200), "iterm_test", "wallpaper_path")
        except Exception as err:
            self.fail(str(err))


class TestTermColor(unittest.TestCase):

    def test_color_format(self):
        with self.assertRaises(exceptions.ColorFormatError):
            TermColorManager([(240, 240, 0.3), (0,0,1)])

    def test_arguments_type(self):
        with self.assertRaises(exceptions.EmptyListError):
            TermColorManager([])

    def test_labels(self):
        """ Asserts that 'get_label' method works properly """
        colors = {
                  (10  , 0.4 , 1 ) : TermColorEnum.RED,
                  (350 , 0.8 , 1 ) : TermColorEnum.RED,
                  (240 , 0   , 0 ) : TermColorEnum.BLUE,
                  (300 , 1   , 1 ) : TermColorEnum.MAGENTA
                 }

        for c in colors:
            self.assertEqual(TermColorManager.get_label(c), colors[c])

    def test_get_color_when_not_enough_labels(self):
        """ Asserts that even if some labels are empty, the program still works """
        input_colors = [
                        (16  , 0.54 , 0.45) , (28  , 0.77 , 0.64) , (45  , 0.94 , 0.66) , (52  , 0.38 , 0.53)
                       ]
        term_colors = TermColorManager([helpers.hsl_to_rgb(c) for c in input_colors])
        try:
            for i in range(16):
                term_colors.get_color(i)
        except Exception as e:
            self.fail(str(e))

    def test_get_color_fails_with_invalid_argument(self):
        """ Checks that 'get_color' fails when called with invalid arguments """
        input_colors = [
                        (16  , 0.54 , 0.45) , (28  , 0.77 , 0.64) , (45  , 0.94 , 0.66) , (52  , 0.38 , 0.53) , \
                       ]

        term_colors = TermColorManager([helpers.hsl_to_rgb(c) for c in input_colors])
        inputs = [-5, 16, "jkl", [], {}, 0.5]
        for i in inputs:
            with self.subTest(line=i):
                with self.assertRaises(exceptions.InvalidValueError):
                    term_colors.get_color(i)


    def test_analyze_colors(self):
        """ Asserts that 'analyze_colors' creates a correct dictionary for a given set of colors """
        input_colors = [
                        (16  , 0.54 , 0.45) , (28  , 0.77 , 0.64) , (45  , 0.94 , 0.66) , (52  , 0.38 , 0.53) , \
                        (59  , 0.97 , 0.67) , (98  , 0.82 , 0.69) , (147 , 0.70 , 0.48) , (162 , 0.60 , 0.42) , \
                        (172 , 0.85 , 0.54) , (177 , 0.64 , 0.39) , (182 , 0.78 , 0.50) , (202 , 0.57 , 0.57) , \
                        (227 , 0.05 , 0.65) , (239 , 0.44 , 0.50) , (305 , 0.70 , 0.50) , (319 , 0.32 , 0.50) , \
                        (333 , 0.57 , 0.42) , (338 , 0.57 , 0.60) , (342 , 0.57 , 0.44) , (344 , 0.60 , 0.5)  , \
                        (348 , 0.92 , 0.62)
                       ]

        expected_dict = {
                TermColorEnum.BLACK   : [(0, 0, 0)],
                TermColorEnum.WHITE   : [(0, 0, 1)],
                TermColorEnum.RED     : [(16, 0.54, 0.45), (348, 0.92, 0.62)],
                TermColorEnum.YELLOW  : [(28, 0.77, 0.64), (45, 0.94, 0.66), (52, 0.38, 0.53), (59, 0.97, 0.67)],
                TermColorEnum.GREEN   : [(98, 0.82, 0.69), (147, 0.70, 0.48)],
                TermColorEnum.CYAN    : [(162, 0.60, 0.42), (172, 0.85, 0.54), (177, 0.64, 0.39), (182, 0.78, 0.50)],
                TermColorEnum.BLUE    : [(202, 0.57, 0.57), (227, 0.05, 0.65), (239, 0.44, 0.50)],
                TermColorEnum.MAGENTA : [(305, 0.70, 0.50), (319, 0.32, 0.50), (333, 0.57, 0.42), (338, 0.57, 0.60), (342, 0.57, 0.44), (344, 0.60, 0.5)]
                }

        colors_dict = TermColorManager.analyze_colors(input_colors)
        for tc in TermColorEnum:
            self.assertEqual(colors_dict[tc], expected_dict[tc])
