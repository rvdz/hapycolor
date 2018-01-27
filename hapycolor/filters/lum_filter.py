from . import base
import warnings
from hapycolor import config, exceptions, helpers
from scipy import interpolate
import math
import numpy as np


class LumFilter(base.Filter):
    # Set up grid
    dark_interp = None
    bright_interp = None

    def interpolate_hyperplans(json_file, filter_type):
        """
        Generates a data structures that represent the interpolated
        luminosity hyperplan (dark or bright).

        .. todo:: This should be replaced by a function that only load a json
        file where that contains the interpolated points instead of
        regenating them each time
        """
        # Load the provided points
        data = helpers.load_json(json_file)
        hsl_points = []
        for s in data:
            for c in data[s][filter_type]:
                hsl_points.append(helpers.rgb_to_hsl(tuple(c)))

        # Adding outer and inner circles for better results
        for h in [22.5*i for i in range(16)]:
            # When the json_file was encoded, some precision has been lost for
            # the hues, this is why we have to ceil the hues
            outer_lum = max(filter(lambda c: c[0] == math.ceil(h)
                                   or c[0] == math.floor(h), hsl_points),
                            key=lambda c: c[1])[2]
            inner_lum = min(filter(lambda c: c[0] == math.ceil(h)
                                    or c[0] == math.floor(h), hsl_points),
                             key=lambda c: c[1])[2]

            # Adding outer circles
            for s in [1.2, 1.5, 1.7, 2]:
                hsl_points.append((h, s, outer_lum))
            # Addding "inner" circle
            hsl_points.append((h, 0, inner_lum))

        # Convert points to catesian
        points = np.asarray([LumFilter.polar_to_cartesian(e) for e in hsl_points])
        x = [e[0] for e in points]
        y = [e[1] for e in points]
        z = [e[2] for e in points]

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
            return interpolate.interp2d(x, y, z, kind="linear")

    def gen_sat_interpolation(json_file):
        # Load the provided points
        data = helpers.load_json(json_file)

        hue_table = {}
        for e in data:
            if e[0] in hue_table:
                hue_table[e[0]].append(e)
            else:
                hue_table[e[0]] = [e]

        hue_interp = {}
        for h in hue_table:
            R = [e[1] for e in hue_table[h]]
            Z = [e[2] for e in hue_table[h]]
            hue_interp[h] = interpolate.interp1d(Z, R, kind="linear")
        return hue_interp

    @staticmethod
    def polar_to_cartesian(polar_point):
        """
        .. warning: The variable's ordering follows the 'hsl' format and not
        the classic (radius, angle, z).
        """
        theta, r, z = polar_point
        # if r < 0 or r > 1 or theta < 0 or theta >= 360 or z < 0 or z > 1:
        #     raise exceptions.NotPolarException("The input tuple does not match"
        #                                        + " polar coordinates")
        return r * np.cos(np.radians(theta)), r * np.sin(np.radians(theta)), z

    @staticmethod
    def apply(palette):
        LumFilter.dark_interp = LumFilter.interpolate_hyperplans(
                config.hyperplan_file(config.Filter.DARK), "dark")

        LumFilter.bright_interp = LumFilter.interpolate_hyperplans(
                config.hyperplan_file(config.Filter.BRIGHT), "bright")

        LumFilter.saturation_interp = LumFilter.gen_sat_interpolation(
                config.hyperplan_file(config.Filter.SATURATION))

        # Set background
        hsl_bg = helpers.rgb_to_hsl(palette.background)
        hsl_bg = (hsl_bg[0], hsl_bg[1], hsl_bg[2]*2)
        if (not LumFilter.is_too_dark(helpers.hsl_to_rgb(hsl_bg))):
            palette.background = (0, 0, 0)
        # if (not LumFilter.is_too_bright(palette.foreground)):
            # palette.background = (255, 255, 255)

        # Set colors
        palette.colors = list(filter(lambda c: not LumFilter.is_too_bright(c)
                              and not LumFilter.is_too_dark(c)
                              and LumFilter.is_enough_saturated(c),
                              palette.colors))
        return palette

    def is_too_bright(rgb_color):
        """
        Returns 'True' if the color is considered too bright, else 'False'.

        :arg hsl_color: a tuple representing an hsl color
        """
        if not helpers.can_be_rgb(rgb_color):
            raise exceptions.ColorFormatError("Color must be defined in the"
                                              + " rgb base")

        hsl_color = helpers.rgb_to_hsl(rgb_color)
        x, y, z = LumFilter.polar_to_cartesian(hsl_color)
        return z > LumFilter.bright_interp(x, y)

    def is_too_dark(rgb_color):
        """
        Returns 'True' if the color is considered too dark, else 'False'.

        :arg rgb_color: a tuple representing an rgb color
        """
        if not helpers.can_be_rgb(rgb_color):
            raise exceptions.ColorFormatError("Color must be defined in the"
                                              + " rgb base")

        hsl_color = helpers.rgb_to_hsl(rgb_color)
        x, y, z = LumFilter.polar_to_cartesian(hsl_color)
        return z < LumFilter.dark_interp(x, y)

    def half_circle_interp(half_circle):
        cartesian_p = [LumFilter.polar_to_cartesian(e) for e in half_circle]
        cartesian_p.sort(key=lambda e: e[0])
        X = [p[0] for p in cartesian_p]
        Y = [p[1] for p in cartesian_p]
        return interpolate.interp1d(X, Y, kind="linear")

    def is_enough_saturated(rgb_color):
        hsl_color = helpers.rgb_to_hsl(rgb_color)
        x, y, z = LumFilter.polar_to_cartesian(hsl_color)

        circle = []
        for h in LumFilter.saturation_interp:
            circle.append((h, LumFilter.saturation_interp[h](z), 0))

        interp_up = LumFilter.half_circle_interp(circle[:len(circle)//2])
        interp_down = LumFilter.half_circle_interp(circle[len(circle)//2:])

        # If the value cannot be interpolated, it means that the point is
        # saturated enough
        try:
            above_upper_half = interp_up(x) > y
            above_bottom_half = interp_down(x) > y
        except ValueError:
            return True
        else:
            return not (above_bottom_half ^ above_upper_half)
