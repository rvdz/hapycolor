from hapycolor import exceptions, helpers, config
import warnings
import pathlib
from tests.helpers import configurationtesting
from hapycolor.filters import lum_filter as lf
from scipy import interpolate
import os
import unittest
import numpy as np
from unittest.mock import patch


class TestLumFilter(unittest.TestCase):
    @configurationtesting()
    def test_hypeplans_files_exist(self):
        """ Checks if manual hyperplan point's file exists """
        for filter_type in lf.Filter:
            hyperplan_file = pathlib.Path(lf.hyperplan_file(filter_type))
            self.assertTrue(hyperplan_file.is_file())

    @configurationtesting()
    def test_hyperplan_files(self):
        with self.assertRaises(exceptions.UnknownLuminosityFilterTypeError):
            lf.hyperplan_file("hue")
        for f in lf.Filter:
            self.assertTrue(pathlib.Path(lf.hyperplan_file(f)).exists())

    def test_polar_to_cartesian(self):
        polar = [(359, 1, 0), (0, 0, 0), (250.0, 1.0, 1.0)]
        cartesian = [[0.9998, -0.017, 0], [0, 0, 0], [-0.342, -0.940, 1.0]]
        not_polar = [(360.0, 1, 0), (0, 1.1, 0), (250, 0, 1.1), (0, -0.1, 0)]

        # This test has been removed since it should convert colors having a
        # saturation higher than 1 (filter optimization)
        # for p in not_polar:
        #     with self.assertRaises(exceptions.NotPolarException):
        #         lf.LumFilter.polar_to_cartesian(p)

        for i, p in enumerate(polar):
            res = lf.LumFilter.polar_to_cartesian(p)
            for j in range(3):
                self.assertAlmostEqual(res[j], cartesian[i][j], 3)


    def polar_to_cartesian(polar_point):
        theta, r, z = polar_point
        return r * np.cos(np.radians(theta)), r * np.sin(np.radians(theta)), z

    @unittest.skip("Needs fixing on Debian")
    def test_interpolation_flat(self):
        """
        Testing a flat hyperplan. All interpolated values should be equal
        to a constant: 0.5

        It does not need to be executed often, it basicaly serves as a
        test that asserts the validity of the interpolation method.
        """
        # Creating flat surface
        colors = []
        for h in [30*i for i in range(360)]:
            for s in [0.5, 0.7, 1, 1.5, 1.2, 2]:
                colors.append((h, s, 0.5))

        points = np.asarray([TestLumFilter.polar_to_cartesian(c) for c in colors])
        x = [c[0] for c in points]
        y = [c[1] for c in points]
        z = [c[2] for c in points]
        # scipy raises:
        # /usr/local/lib/python3.6/site-packages/scipy/interpolate/_fitpack_impl.py:975:
        # RuntimeWarning: No more knots can be added because the number of B-spline
        # coefficients already exceeds the number of data points m.
        # Probable causes: either s or m too small. (fp>s)
	#       kx,ky=1,1 nx,ny=16,14 m=160 fp=0.004157 s=0.000000
        # warnings.warn(RuntimeWarning(_iermess2[ierm][0] + _mess))
        #
        # I don't really know how to avoid that, so I'll just silence it,
        # seems wise enough to me
        with warnings.catch_warnings(record=True) as w:
            f = interpolate.interp2d(x, y, z, kind="linear")

        # Creating test colors
        polar_points = []
        for h in range(360):
            for s in np.linspace(0, 1, 10):
                polar_points.append((h, s, 0))
        points = [lf.LumFilter.polar_to_cartesian(p) for p in polar_points]

        # Testing
        for p in points:
            lum_interp = f(p[0], p[1])
            self.assertLess(lum_interp[0], 0.55)
            self.assertGreater(lum_interp[0], 0.45)

    saturation_hyperplan = [(0, 0.3, 0), (0, 0.3, 0.5), (0, 0.3, 1),
                            (90, 0.3, 0), (90, 0.3, 0.5), (90, 0.3, 1),
                            (180, 0.3, 0), (180, 0.3, 0.5), (180, 0.3, 1),
                            (270, 0.3, 0), (270, 0.3, 0.5), (270, 0.3, 1)]

    @patch("hapycolor.helpers.load_json",
           return_value=saturation_hyperplan)
    def test_gen_sat_interpolation(self, mock_hyperplan):
        interp = lf.LumFilter.gen_sat_interpolation("")
        for h in interp:
            self.assertAlmostEqual(interp[h](0), 0.3, 3)
            self.assertAlmostEqual(interp[h](0.2), 0.3, 3)
            self.assertAlmostEqual(interp[h](0.5), 0.3, 3)
            self.assertAlmostEqual(interp[h](1), 0.3, 3)

    def test_half_circle_interp(self):
        """
        Tests the interpolation of a circle on the space (hues, saturation)
        for a fixed luminosity.
        """
        circle = [(0, 0.3, 0.5), (60, 0.3, 0.5), (120, 0.3, 0.5),
                  (180, 0.3, 0.5), (240, 0.3, 0.5), (300, 0.3, 0.5)]
        up = lf.LumFilter.half_circle_interp(circle[:len(circle)//2])
        down = lf.LumFilter.half_circle_interp(circle[len(circle)//2:])

        white_p = [(0, 0, 0.5), (30, 0.1, 0.5), (350, 0.2, 0.5),
                   (200, 0.25, 0.5), (150, 0.28, 0.5)]
        cartesian_white = [lf.LumFilter.polar_to_cartesian(c) for c in white_p]

        saturated_p = [(0, 0.5, 0.5), (0, 0.4, 0.5), (200, 0.7, 0.5),
                       (300, 1, 0.5), (100, 0.4, 0.5)]
        cartesian_sat = [lf.LumFilter.polar_to_cartesian(c) for c in
                         saturated_p]
        for p in cartesian_white:
            above_0 = up(cartesian_white[0][0]) < cartesian_white[0][1]
            above_1 = down(cartesian_white[0][0]) < cartesian_white[0][1]
            self.assertTrue(above_0 ^ above_1)

        for p in cartesian_sat:
            try:
                above_0 = up(cartesian_sat[0][0]) < cartesian_sat[0][1]
                above_1 = down(cartesian_sat[0][0]) < cartesian_sat[0][1]
            except ValueError:
                pass
            else:
                self.assertFalse(above_0 ^ above_1)

    def test_analyze_inputs(self):
        # HSL input format instead of RGB
        color_inputs = [
                        ((0, 0.5, 1), "brightness"),
                        ((300, 1, 1), "brightness"),
                       ]

        # Invalid type of analysis
        kind_inputs = [
                       ((200, 200, 200), "asdfjk"),
                       ((100, 100, 100), "")
                      ]

        for i in color_inputs:
            with self.assertRaises(exceptions.ColorFormatError):
                lf.LumFilter.analyze(i[0], i[1])

        for i in kind_inputs:
            with self.assertRaises(exceptions.UnknownAnalysisTypeException):
                lf.LumFilter.analyze(i[0], i[1])

    @configurationtesting()
    def test_limit_cases_bright(self):
        lf.LumFilter.bright_interp = lf.LumFilter.interpolate_hyperplans(
                lf.hyperplan_file(lf.Filter.BRIGHT), "bright")
        bright = [(0, 0, 1), (12, 1, 0.9), (240, 1, 0.95), (0, 0.5, 0.9)]
        for c in [helpers.hsl_to_rgb(c) for c in bright]:
            self.assertTrue(lf.LumFilter.analyze(c, "brightness"))

        not_bright = [(0, 1, 0.2), (150, 0.5, 0.5), (250, 0.2, 0.2), (50, 0.2, 0.1),
                      (300, 0.9, 0.1), (275, 0, 0.2), (40, 1, 0.4), (30, 0.9, 0.1),
                      (0, 0.5, 0), (50, 0, 0), (100, 1, 0), (0, 0, 0)]
        for c in [helpers.hsl_to_rgb(c) for c in not_bright]:
            self.assertFalse(lf.LumFilter.analyze(c, kind="brightness"))

    @configurationtesting()
    def test_interpolated_dark(self):
        """
        Asserts that the interpolation function for the dark colors, is valid
        for at least 20% of the colors
        """
        lf.LumFilter.initialization()
        errors, total = TestLumFilter.interpolate_colors(
                lf.LumFilter.dark_interp, lambda l: l > 0.5)
        self.assertLess(errors, total // 5)

    @configurationtesting()
    def test_interpolated_bright(self):
        """
        Asserts that the interpolation function for the bright colors, is valid
        for at least 20% of the colors
        """
        lf.LumFilter.initialization()
        errors, total = TestLumFilter.interpolate_colors(
                lf.LumFilter.bright_interp, lambda l: l < 0.5)
        self.assertLess(errors, total // 5)

    def interpolate_colors(interp, predicate):
        error_count = 0
        hues_divisions = 36
        saturation_divisions = 10
        for h in np.linspace(0, 360, hues_divisions):
            for s in np.linspace(0, 1, saturation_divisions):
                x, y, z = lf.LumFilter.polar_to_cartesian((h, s, 0))
                z = interp(x, y)
                if predicate(z):
                    error_count += 1
        return (error_count, hues_divisions * saturation_divisions)


    @configurationtesting()
    def test_limit_cases_dark(self):
        lf.LumFilter.dark_interp = lf.LumFilter.interpolate_hyperplans(
                lf.hyperplan_file(lf.Filter.DARK), "dark")

        dark = [(0, 0, 0), (240, 1, 0.1), (81, 1, 0.1), (300, 1, 0.1), (0, 1, 0),
                (300, 0.5, 0.1), (150, 0.38, 0.03), (358, 0.86, 0.12)]
        for c in [helpers.hsl_to_rgb(c) for c in dark]:
            self.assertTrue(lf.LumFilter.analyze(c, kind="darkness"))

        not_dark = [(0, 0, 1), (0, 1, 1), (300, 0.5, 0.7), (0, 0, 0.5), (200, 0.2, 0.6)]
        for c in [helpers.hsl_to_rgb(c) for c in not_dark]:
            self.assertFalse(lf.LumFilter.analyze(c, kind="darkness"))
