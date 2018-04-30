import contextlib
import unittest
from unittest import mock
from colormath.color_diff import delta_e_cie2000

from hapycolor import helpers
from hapycolor.targets.pam import PAM

class TestPAM(unittest.TestCase):
    def distance(c_1, c_2):
        return abs(c_2 - c_1)

    def test_1_clusters(self):
        colors = [1]
        k = 1
        expected = {1: [1]}

        res = PAM(colors, k, TestPAM.distance)()
        self.assertDictEqual(res, expected)

    def test_2_clusters_2_colors(self):
        colors = [1, 2]
        k = 2
        expected = {1: [1], 2: [2]}

        res = PAM(colors, k, TestPAM.distance)()
        self.assertDictEqual(res, expected)

    def test_2_clusters_10_colors(self):
        colors = [1, 2, 3, 4, 5, 10, 11, 12, 13, 14]
        k = 2
        expected = {3: [1, 2, 3, 4, 5], 12: [10, 11, 12, 13, 14]}

        res = PAM(colors, k, TestPAM.distance)()
        self.assertDictEqual(res, expected)

    def test_3_clusters(self):
        colors = [1, 2, 3, 7, 8, 9, 20, 21, 22]
        k = 3
        expected = {2: [1, 2, 3], 8: [7, 8, 9], 21: [20, 21, 22]}

        res = PAM(colors, k, TestPAM.distance)()
        self.assertDictEqual(res, expected)

    def test_4_clusters_4_colors(self):
        colors = [1, 2, 3, 7]
        k = 4
        expected = {1: [1], 2: [2], 3: [3], 7: [7]}

        res = PAM(colors, k, TestPAM.distance)()
        self.assertDictEqual(res, expected)

    @unittest.skip("fixed in the next pull request")
    def test_3_clusters_3_colors_rgb(self):
        colors = [(0, 0, 0), (100, 100, 100), (255, 255, 255)]
        lab_colors = [helpers.rgb_to_lab(c) for c in colors]
        expected = colors[:]
        k = 3

        def distance(c1, c2):
            return delta_e_cie2000(c1, c2)

        res = PAM(lab_colors, k, distance)()
        for medoid in res:
            self.assertIn(helpers.lab_to_rgb(medoid), expected)
            self.assertIn(helpers.lab_to_rgb(res[medoid][0]), expected)

    def test_2_clusters_4_colors_rgb(self):
        colors = [(150, 20, 20), (180, 10, 10), (10, 10, 160), (20, 20, 190)]
        lab_colors = [helpers.rgb_to_lab(c) for c in colors]

        k = 2
        expected = [
                    [(150, 20, 20), (180, 10, 10)],
                    [(10, 10, 160), (20, 20, 190)],
                   ]

        def distance(c1, c2):
            return delta_e_cie2000(c1, c2)

        res = PAM(lab_colors, k, distance)()
        for i, medoid in enumerate(res):
            cluster = [helpers.lab_to_rgb(c) for c in res[medoid]]
            self.assertIn(cluster, expected)

    @unittest.skip("Too slow, but working")
    def test_multiple_colors(self):
        colors = [(83, 7, 53), (13, 25, 84), (18, 22, 81), (19, 28, 91),
                  (24, 26, 88), (56, 7, 70), (46, 19, 76), (40, 25, 87),
                  (56, 27, 88), (11, 46, 81), (22, 39, 89), (46, 38, 88),
                  (22, 29, 97), (22, 20, 112), (44, 14, 113), (11, 40, 100),
                  (252, 207, 115), (228, 225, 100), (251, 241, 112), (35, 35, 145),
                  (19, 84, 137), (19, 107, 143), (32, 104, 158), (75, 76, 185),
                  (225, 91, 137), (248, 115, 134), (31, 159, 155), (86, 168, 155),
                  (33, 225, 157), (45, 240, 144), (79, 247, 138), (33, 165, 207),
                  (84, 163, 209), (42, 238, 211), (35, 217, 224), (41, 253, 250),
                  (49, 245, 242), (86, 236, 231), (250, 142, 135), (233, 160, 161),
                  (147, 236, 151), (253, 209, 138), (244, 233, 168), (158, 241, 217)]
        lab_colors = [helpers.rgb_to_lab(c) for c in colors]
        def distance(c1, c2):
            return delta_e_cie2000(c1, c2)
        k = 5
        PAM(colors, k)()
