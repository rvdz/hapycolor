import unittest
from hapycolor.targets.eight_bit_colors import short2rgb, rgb2short

class TestEightBitColors(unittest.TestCase):
    def test_short_to_rgb(self):
        self.assertEqual(short2rgb(254), (228, 228, 228))
        self.assertEqual(short2rgb(208), (255, 135, 0))
        self.assertEqual(short2rgb(160), (215, 0, 0))
        self.assertEqual(short2rgb(1),  (128, 0, 0))
        self.assertEqual(short2rgb(9),  (255, 0, 0))
