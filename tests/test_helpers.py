import unittest
import helpers

class UtilsTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_hsl_to_rgb(self):
        colors = []
        colors.append((0, 0, 0))
        colors.append((360, 1, 1))
        colors.append((22, 0.111111111111, 0.99999))

        for c in colors:
            self.__test_rgb_color(helpers.hsl_to_rgb(c))

    def __test_rgb_color(self, color):
        self.assertEqual(len(color), 3)
        for c in color:
            self.assertTrue(0 <= c and c <= 255)

    def __test_hsl_color(self, color):
        self.assertEqual(len(color), 3)

        self.assertTrue(0 <= color[0] and color[0] <= 360)
        self.assertTrue(0 <= color[1] and color[1] <= 1)
        self.assertTrue(0 <= color[2] and color[2] <= 1)

    def test_rgb_to_hsl(self):
        colors = []
        colors.append((0, 0, 0))
        colors.append((255, 255, 255))
        colors.append((12, 3, 5))

        for c in colors:
            self.__test_hsl_color(helpers.rgb_to_hsl(c))
