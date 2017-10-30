from hapycolor import palette
from hapycolor import exceptions

import unittest

class TestPalette(unittest.TestCase):

    def test_invalid_background_and_foreground(self):
        pltte = palette.Palette()
        formats = [[], {}, (1,2,3,4), (350, 0, 0), (0,0,0.4)]
        for f in formats:
            with self.subTest(line=f):
                with self.assertRaises(exceptions.ColorFormatError):
                    pltte.foreground = f
                with self.assertRaises(exceptions.ColorFormatError):
                    pltte.background = f

    def test_valid_background_and_foreground(self):
        pltte = palette.Palette()
        formats = [(0,0,0), (245, 0, 1)]
        try:
            for f in formats:
                pltte.foreground = f
                pltte.background = f
        except Exception as e:
            self.fail(str(e))


    def test_invalid_colors(self):
        pltte = palette.Palette()
        formats = [[], [(350, 0, 0)], [(24, 24, 24), (2, 0.5, 1)], [{}]]
        for f in formats:
            with self.subTest(line=f):
                with self.assertRaises(exceptions.ColorFormatError):
                    pltte.colors = f

    def test_valid_colors(self):
        pltte = palette.Palette()
        formats = [[(0, 0, 0), (255, 255, 255)], [(2, 2, 2)]]
        try:
            for f in formats:
                with self.subTest(line=f):
                        pltte.colors = f
        except Exception as e:
            self.fail(str(e))
