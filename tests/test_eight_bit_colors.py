from hapycolor.targets.eight_bit_colors import short_to_rgb
import unittest


class TestEightBitColors(unittest.TestCase):
    def test_short_to_rgb(self):
        self.assertEqual(short_to_rgb(254), (228, 228, 228))
        self.assertEqual(short_to_rgb(208), (255, 135, 0))
        self.assertEqual(short_to_rgb(160), (215, 0, 0))
        self.assertEqual(short_to_rgb(1),  (128, 0, 0))
        self.assertEqual(short_to_rgb(9),  (255, 0, 0))
