import unittest
import color_filter
from config import Config, FilterEnum
import os
import helpers

class FilterUnitTest(unittest.TestCase):
    def setUp(self):
        self.cf = color_filter.ColorFilter()


    def test_manual_hypeplan_point_exist(self):
        """ Checks if manual hyperplan point's file exists """
        for filter_type in FilterEnum:
            self.assertTrue(os.path.isfile(Config.get_hyperplan_file(filter_type)))


    def test_json_manual_points(self):
        """ Checks if the provided point from which are generated the hyperplans
            are valid """
        for filter_type in FilterEnum:
            self.__test_json_manual_points_single(Config.get_hyperplan_file(filter_type))


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
        self.assertNotEqual(len(self.cf.X), 0)
        self.assertNotEqual(len(self.cf.Y), 0)

    def test_grey_hyperplan(self):
        """ Checks that the luminosities ot the grey hyperplan are correctly bounded """
        for key in self.cf.grey_interpolation:
            self.assertTrue(0 <= key and key <= 1)
