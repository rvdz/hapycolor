from hapycolor import helpers
from hapycolor import config
from hapycolor.color import filter as fltr

import pathlib
import unittest

class TestFilter(unittest.TestCase):
    def setUp(self):
        self.fltr = fltr.Filter()


    def test_json_manual_points(self):
        """ Checks if the provided point from which are generated the hyperplans
            are valid """
        for filter_type in config.Filter:
            self.__test_json_manual_points_single(config.hyperplan_file(filter_type))


    def __test_json_manual_points_single(self, json_file):
        data = helpers.load_json(json_file)
        self.assertTrue(len(data) >= 100)
        H = [e[0] for e in data]
        S = [e[1] for e in data]
        L = [e[2] for e in data]

        for h in H:
            self.assertTrue(0 <= h and h <= 360)
        for s in S:
            self.assertTrue(0 <= s and s <= 1)
        for l in L:
            self.assertTrue(0 <= l and l <= 1)

    def test_grid_creation(self):
        """ Checks if the grid defining the interpolated hypeplan is created """
        self.assertNotEqual(len(self.fltr.X), 0)
        self.assertNotEqual(len(self.fltr.Y), 0)

    def test_grey_hyperplan(self):
        """ Checks that the luminosities ot the grey hyperplan are correctly bounded """
        for key in self.fltr.grey_interpolation:
            self.assertTrue(0 <= key and key <= 1)

    def __test_hyperplan(self, colors_answers, filter_function):
        for c, expected_ans in colors_answers.items():
            with self.subTest(line=c):
                self.assertEqual(filter_function(c), expected_ans)

    def test_is_too_bright(self):
        """ Tests some limit cases for 'is_too_bright' """
        colors = {
                  (0, 0, 0)     : False,
                  (0, 0, 1)     : True,
                  (359, 0, 0.3) : False
                 }
        self.__test_hyperplan(colors, self.fltr.is_too_bright)


    def test_is_too_dark(self):
        """ Tests some limit cases for 'is_too_dark' """
        colors = {
                  (0, 0, 0)     : True,
                  (0, 0, 1)     : False,
                  (359, 0, 0.8) : False
                 }
        self.__test_hyperplan(colors, self.fltr.is_too_dark)

    def test_is_saturated_enough(self):
        """ Tests some limit cases for 'is_saturated_enough' """
        colors = {
                  (359, 1, 0.5)   : True,
                  # (250, 0, 0.5) : False,
                  (250, 0.8, 0.5) : True
                 }
        self.__test_hyperplan(colors, self.fltr.is_saturated_enough)
