import warnings
import enum
import math
from scipy import interpolate
import numpy as np
from hapycolor import config, exceptions, helpers
from . import base


class Filter(enum.Enum):
    BRIGHT = 1
    DARK = 2
    SATURATION = 3


def hyperplan_file(filter_type):
    configuration = config.ConfigurationManager.load("hyperplan")
    path = config.ROOT_DIR
    if filter_type == Filter.DARK:
        path /= configuration["dark"]
    elif filter_type == Filter.BRIGHT:
        path /= configuration["bright"]
    elif filter_type == Filter.SATURATION:
        path /= configuration["saturation"]
    else:
        msg = "Unknown filter type"
        raise exceptions.UnknownLuminosityFilterTypeError(msg)
    return path.as_posix()


class LumFilter(base.Filter):
    # Set up grid
    dark_interp = None
    dark_max = None

    bright_interp = None
    bright_min = None

    def interpolate_hyperplans(json_file, filter_type):
        """
        Generates a data structures that represent the interpolated
        luminosity hyperplan (dark or bright).

        .. todo::
            This should be replaced by a function that only load a json
            file where that contains the interpolated points instead of
            regenating them each time
        """
        # Load the provided points
        data = helpers.load_json(json_file)
        hsl_points = []
        for s in data:
            for c in data[s][filter_type]:
                hsl_points.append(helpers.rgb_to_hsl(tuple(c)))

        if filter_type == "bright":
            LumFilter.bright_min = min(hsl_points, key=lambda c: c[2])[2]
        elif filter_type == "dark":
            LumFilter.dark_max = max(hsl_points, key=lambda c: c[2])[2]

        hues_step = 22.5
        hues_divisions = 16
        # Adding outer and inner circles for better results
        for h in [hues_step * i for i in range(hues_divisions)]:
            # When the json_file was encoded, some precision has been lost for
            # the hues, this is why we have to ceil or floor the hues
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
        points = np.asarray([LumFilter.polar_to_cartesian(e)
                            for e in hsl_points])
        x = [e[0] for e in points]
        y = [e[1] for e in points]
        z = [e[2] for e in points]

        # scipy raises:
        # /usr/local/lib/python3.6/site-packages/scipy/interpolate/_fitpack_impl.py:975:
        # RuntimeWarning: No more knots can be added because the number of
        # B-spline coefficients already exceeds the number of data points m.
        # Probable causes: either s or m too small. (fp>s)
        # kx,ky=1,1 nx,ny=16,14 m=160 fp=0.004157 s=0.000000
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
        .. warning::
            The variable's ordering follows the 'hsl' format and not
            the classic (radius, angle, z).
        """
        theta, r, z = polar_point
        # if r < 0 or r > 1 or theta < 0 or theta >= 360 or z < 0 or z > 1:
        #     raise exceptions.NotPolarException("The input tuple does not"
        #                                        + "match polar coordinates")
        return r * np.cos(np.radians(theta)), r * np.sin(np.radians(theta)), z

    def initialization():
        """
        Initializes the interpolation functions and the max/min values of
        the dark/bright surfaces
        """
        LumFilter.dark_interp = LumFilter.interpolate_hyperplans(
                hyperplan_file(Filter.DARK), "dark")

        LumFilter.bright_interp = LumFilter.interpolate_hyperplans(
                hyperplan_file(Filter.BRIGHT), "bright")

        LumFilter.saturation_interp = LumFilter.gen_sat_interpolation(
                hyperplan_file(Filter.SATURATION))

    @staticmethod
    def apply(palette):
        LumFilter.initialization()

        # Set background
        hsl_bg = helpers.rgb_to_hsl(palette.background)
        hsl_bg = (hsl_bg[0], hsl_bg[1], hsl_bg[2]*2)
        if not LumFilter.analyze(helpers.hsl_to_rgb(hsl_bg), "darkness"):
            palette.background = (0, 0, 0)
        # if (not LumFilter.is_too_bright(palette.foreground)):
            # palette.background = (255, 255, 255)

        # Set colors
        palette.colors = list(filter(lambda c:
                              not LumFilter.analyze(c, "brightness")
                              and not LumFilter.analyze(c, "darkness")
                              and not LumFilter.analyze(c, "saturation"),
                              palette.colors))
        return palette

    def analyze(rgb_color, kind):
        """
        Analyzes a provided color according to a specific type of analysis. It
        can be: brightness, darkness or saturation.

        :arg rgb_color: The input color to be analyzed.
        :arg kind: Type of analysis available: 'brightness', 'darkness' or
            'saturation'.
        :return: This function will return 'True' if the color is too bright,
            too dark, or not enough satured, else, 'False'.
        """
        if not helpers.can_be_rgb(rgb_color):
            raise exceptions.ColorFormatError("Color must be defined in the"
                                              + " rgb base")

        hsl_color = helpers.rgb_to_hsl(rgb_color)
        x, y, z = LumFilter.polar_to_cartesian(hsl_color)

        if kind == "brightness":
            return z > LumFilter.bright_min \
                   or z > LumFilter.bright_interp(x, y)
        elif kind == "darkness":
            return z < LumFilter.dark_max or z < LumFilter.dark_interp(x, y)
        elif kind == "saturation":
            return not LumFilter.is_enough_saturated(rgb_color)
        else:
            msg = str(kind) + "is not a supported analysis type"
            raise exceptions.UnknownAnalysisTypeException(msg)

    def half_circle_interp(half_circle):
        cartesian_p = [LumFilter.polar_to_cartesian(e) for e in half_circle]
        cartesian_p.sort(key=lambda e: e[0])
        X = [p[0] for p in cartesian_p]
        Y = [p[1] for p in cartesian_p]
        return interpolate.interp1d(X, Y, kind="linear")

    def is_enough_saturated(rgb_color):
        """
        To interpolate the saturation that separates the saturated enough
        colors with those that aren't, for a specific hue and luminosity,
        some 2D points (hue, saturation), are interpolated for the same
        luminosity (the one of the provided argument), and should form a
        circle. Then, this circle is divided into an upper circle and a
        bottom circle, from which an interpolation function can be computed
        with `scipy`. With these two functions, it is possible to assert if a
        color is saturated enough.
        """
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
