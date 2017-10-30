import unittest
import contextlib
from unittest.mock import patch

from hapycolor import exceptions
from hapycolor.color import extractor

@contextlib.contextmanager
def disableprints():
    with patch('hapycolor.visual.print_palette') as mock_print_palette, \
            patch('builtins.print') as mock_print:
        yield

class TestExtractor(unittest.TestCase):

    def test_initialization(self):
        try:
            extractor.Extractor("./tests/images/taipei.jpg", 200)
        except Exception as err:
            self.fail(str(err))

    def test_invalid_image(self):
        with self.assertRaises(exceptions.InvalidImageError):
            extractor.Extractor(".", 200)

    def test_invalid_argument_types(self):
        with self.assertRaises(exceptions.ExtractorArgumentsError):
            extractor.Extractor(12, 23)
        with self.assertRaises(exceptions.ExtractorArgumentsError):
            extractor.Extractor("jk", "num")

    def test_invalid_image(self):
        with self.assertRaises(exceptions.InvalidImageError):
            extractor.Extractor(".", 12)

    def test_0_color_input(self):
        with self.assertRaises(exceptions.ExtractorArgumentsError):
            extractor.Extractor("./tests/images/taipei.jpg", 0)
        with self.assertRaises(exceptions.ExtractorArgumentsError):
            extractor.Extractor("./tests/images/taipei.jpg", -15)

    @disableprints()
    def test_get_colors(self):
        try:
            extrct = extractor.Extractor("./tests/images/taipei.jpg", 16)
            extrct.get_colors()
        except Exception as err:
            self.fail(str(err))
