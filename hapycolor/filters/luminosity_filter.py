from hapycolor import config
from hapycolor import helpers
from hapycolor import exceptions
from . import base

from matplotlib import pyplot as plt
from scipy import interpolate
import numpy as np
import sys


class LuminosityFilter(base.Filter):
    # Set up grid
    grid_x, grid_y = np.mgrid[-1:1:100j, -1:1:100j]
    X              = [x[0] for x in grid_x]
    Y              = grid_y[0]

    dark_Z = None

    bright_Z = None

    @staticmethod
    def __generate_luminosity_hyperplan(json_file, grid_x, grid_y):
        """
        Generates a data structures that represent the interpolated
        luminosity hyperplan (dark or bright)
        TODO: This should be replaced by a function that only load a json
        file where that contains the interpolated points instead of
        regenating them each time
        """
        # Load the provided points
        data = helpers.load_json(json_file)

        # Convert points to catesian
        cartesian_p = [LuminosityFilter.__polar_to_cartesian(e[0], e[1]) for e in data]
        points = np.asarray(cartesian_p)
        values = [e[2] for e in data]

        # Interpolate the data
        return interpolate.griddata(points, values, (grid_x, grid_y),
                                    method='linear')


    @staticmethod
    def __polar_to_cartesian(r, theta, z=0):
        return r * np.cos(np.radians(theta)), r * np.sin(np.radians(theta))

    @staticmethod
    def __find_nearest_index(value, vector):
        i = 0
        for i, v in enumerate(vector):
            if v > value:
                return i
        return i

    @staticmethod
    def __find_nearest_point(P, surface_values):
        """ Returns the luminosity of the nearest interpolated point of
            the given point P """
        real_points = []
        for i in range(len(LuminosityFilter.X)):
            # Search nearest point of the upper portion of the circle
            j = 0
            while surface_values[i, j] != surface_values[i, j]:
                # If there are no values along this axis
                j += 1
                if j + 1 > len(LuminosityFilter.Y):
                    break

            # If there are no values along this axis
            if j + 1 > len(LuminosityFilter.Y):
                continue

            real_points.append((i, j))
            # Search nearest point of the lower portion of the circle
            j = len(LuminosityFilter.Y) - 1
            while surface_values[i, j] != surface_values[i, j]:
                j -= 1
            real_points.append([i, j])

        distance = sys.maxsize
        nearest_point = ()
        for p in real_points:
            if LuminosityFilter.__get_2d_distance(P, p) < distance:
                distance = LuminosityFilter.__get_2d_distance(P, p)
                nearest_point = p
        return surface_values[nearest_point[0], nearest_point[1]]

    @staticmethod
    def __get_2d_distance(p1, p2):
        return pow(p1[0] - p2[0], 2) + pow(p1[1] - p2[1], 2)

    @staticmethod
    def __project_point(x, y, surface_values):
        index_x = LuminosityFilter.__find_nearest_index(x, LuminosityFilter.X)
        index_y = LuminosityFilter.__find_nearest_index(y, LuminosityFilter.Y)

        interpol_value = surface_values[index_x, index_y]

        # If there are no interpolated values for this point, find the nearest
        if interpol_value != interpol_value:
            interpol_value = LuminosityFilter.__find_nearest_point((x, y), surface_values)

        return interpol_value

    @staticmethod
    def apply(palette):
        LuminosityFilter.dark_Z = LuminosityFilter.__generate_luminosity_hyperplan(
                            config.hyperplan_file(config.LuminosityFilter.DARK),
                            LuminosityFilter.grid_x, LuminosityFilter.grid_y)

        LuminosityFilter.bright_Z = LuminosityFilter.__generate_luminosity_hyperplan(
                            config.hyperplan_file(config.LuminosityFilter.BRIGHT),
                            LuminosityFilter.grid_x, LuminosityFilter.grid_y)

        palette.colors = list(filter(lambda c: not LuminosityFilter.is_too_bright(c) \
                                               and not LuminosityFilter.is_too_dark(c) \
                                               and helpers.rgb_to_hsl(c)[1] > 0.3, palette.colors))

        hsl_bg = helpers.rgb_to_hsl(palette.background)
        hsl_bg = (hsl_bg[0], hsl_bg[1], hsl_bg[2]*2)
        if (not LuminosityFilter.is_too_dark(helpers.hsl_to_rgb(hsl_bg))):
            palette.background = (0, 0, 0)
        if (not LuminosityFilter.is_too_bright(palette.foreground)):
            palette.background = (255, 255, 255)

        return palette


    @staticmethod
    def is_too_bright(rgb_color):
        """
        Returns 'True' if the color is considered too bright, else 'False'.

        Keyword arguments:
        hsl_color -- a tuple representing an hsl color
        """
        if not helpers.can_be_rgb(rgb_color):
            raise exceptions.ColorFormatError("Color must be defined in the rgb base")

        hsl_color = helpers.rgb_to_hsl(rgb_color)
        x, y = LuminosityFilter.__polar_to_cartesian(hsl_color[0], hsl_color[1])
        return hsl_color[2] > LuminosityFilter.__project_point(x, y, LuminosityFilter.bright_Z)

    @staticmethod
    def is_too_dark(rgb_color):
        """
        Returns 'True' if the color is considered too dark, else 'False'.

        Keyword arguments:
        rgb_color -- a tuple representing an rgb color
        """
        if not helpers.can_be_rgb(rgb_color):
            raise exceptions.ColorFormatError("Color must be defined in the rgb base")

        hsl_color = helpers.rgb_to_hsl(rgb_color)
        x, y = LuminosityFilter.__polar_to_cartesian(hsl_color[0], hsl_color[1])
        return hsl_color[2] < LuminosityFilter.__project_point(x, y, LuminosityFilter.dark_Z)
