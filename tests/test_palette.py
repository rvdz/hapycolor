from hapycolor import palette, exceptions, helpers
import unittest
from tests.helpers import disableprints
import os


class TestPalette(unittest.TestCase):
    def test_invalid_background_and_foreground(self):
        pltte = palette.Palette()
        formats = [[], {}, (1, 2, 3, 4), (350, 0, 0), (0, 0, 0.4)]
        for f in formats:
            with self.subTest(line=f):
                with self.assertRaises(exceptions.ColorFormatError):
                    pltte.foreground = f
                with self.assertRaises(exceptions.ColorFormatError):
                    pltte.background = f

    def test_valid_background_and_foreground(self):
        pltte = palette.Palette()
        formats = [(0, 0, 0), (245, 0, 1)]
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

    @disableprints()
    def test_json_conversion(self):
        pltte = palette.Palette()
        pltte.foreground = (255, 255, 255)
        pltte.background = (0, 0, 0)
        colors = [
                  [(12, 12, 12), (15, 15, 15), (17, 16, 16)],
                  [(0, 0, 0)],
                 ]
        json_file = "./tests/test_palette.json"
        for c in colors:
            pltte.colors = c
            pltte.to_json(json_file)
            new_palette = palette.Palette.from_json(json_file)
            self.assertEqual(new_palette.foreground, pltte.foreground)
            self.assertEqual(new_palette.background, pltte.background)
            self.assertEqual(new_palette.colors, pltte.colors)
        os.remove(json_file)
