from scipy.interpolate import griddata
from  matplotlib import pyplot as plt
from utils import hsl_to_rgb
import numpy as np
import json
from sys import argv, maxint

from platform import system
from ctypes import cdll, c_uint, c_char_p


class ColorFilter():

    def __init__(self):
        dark_hyperplan = "dark.json"

        # Set up grid
        grid_x, grid_y = np.mgrid[-1:1:100j, -1:1:100j]
        self.X = [x[0] for x in grid_x]
        self.Y = grid_y[0]

        # Load the provided points
        data = self.__load_points(dark_hyperplan)
        points, values = self.__polar_to_cartesian(data)

        # Interpolate the data
        self.dark_Z = griddata(points, values, (grid_x, grid_y), method='linear')

        # Library defining a maximal clique algorithm
        if system() == "Darwin":
            self.lib = cdll.LoadLibrary("./libcolor_reducer.dylib")
        else:
            self.lib = cdll.LoadLibrary("./libcolor_reducer.so")

    def __polar_to_cartesian(self, data):
        """ Converts points defined in a polar base to a cartesian base
            Returns the points in a numpy array """
        points = []
        values = []
        for e in data:
            points.append(
                    [e[1] * np.cos(np.radians(e[0])),
                     e[1] * np.sin(np.radians(e[0])) ] )
            values.append(e[2])
        return np.asarray(points), np.asarray(values)

    def __load_points(self, file_path):
        """ Load hsl points stored in a json file """
        with open(file_path) as f:
            data = json.load(f)
        return data

    def __display_interpolation():
        """ Displays the wireframe of a surface """
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_wireframe(self.X, self.Y, self.dark_Z) #, cmap=plt.cm.YlGnBu_r)
        plt.show()

    def __display_surface(self, X, Y, Z, colors):
        """ Displays a scatter plot where each color is represented by a
        a color of the given list """
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(X, Y, Z, c=colors)
        plt.show()

    def __find_nearest_index(self, value, vector):
        i = 0
        while vector[i] < value:
            i += 1
        return i

    def __find_nearest_point(self, P):
        """ Returns the luminosity of the nearest interpolated point of
            the given point P """
        real_points = []
        for i in range(len(self.X)):
            # Search nearest point of the upper portion of the circle
            j = 0
            while self.dark_Z[i, j] !=  self.dark_Z[i, j]:
                # If there are no values along this axis
                j += 1
                if j + 1 > len(self.Y):
                    break

            if j + 1 > len(self.Y):
                continue
            real_points.append([i, j])
            # Search nearest point of the lower portion of the circle
            j = len(self.Y) - 1
            while self.dark_Z[i, j] != self.dark_Z[i, j]:
                j -= 1
            real_points.append([i, j])

        distance = maxint
        nearest_point = []
        for p in real_points:
            if self.__get_2d_distance(P, p) < distance:
                distance = self.__get_2d_distance(P, p)
                nearest_point = p
        return self.dark_Z[nearest_point[0], nearest_point[1]]

    def __get_2d_distance(self, p1, p2):
        return pow(p1[0] - p2[0], 2) + pow(p1[1] - p2[1], 2)

    def __project_point(self, x, y):

        index_x = self.__find_nearest_index(x, self.X)
        index_y = self.__find_nearest_index(y, self.Y)

        dark_projection_value = self.dark_Z[index_x, index_y]
        bright_projection_value = 0

        # If there are no interpolated values for this point, find the nearest
        if self.dark_Z[index_x, index_y] != self.dark_Z[index_x, index_y]:
            dark_projection_value = self.__find_nearest_point([x, y])

        return (dark_projection_value, bright_projection_value)

    def is_too_bright(self, hsl_color):
        """ Returns a boolean depending if the given color is too bright.
            The color provided must be in hsl format"""
        [point], [val] =  self.__polar_to_cartesian([hsl_color])
        val > self.__project_point(point[0], point[1])[1]
        return False

    def is_too_dark(self, hsl_color):
        """ Returns a boolean depending if the given color is too dark.
            The color provided must be in hsl format"""
        [point], [val] =  self.__polar_to_cartesian([hsl_color])
        return val < self.__project_point(point[0], point[1])[0]



    def __decode_colors_id(self, string, input_colors):
        """ Decode a string where an integer is encoded over four bytes.
            The even ones contain either '\x01' or '\x02' if the following
            value is null. The odd ones contain a dummy value if it should
            be null, or the actual value """
        colors = []
        i = 0
        while i < len(string):
            index = 0
            if string[i] == '\x02':
                index = ord(string[i + 1]) * 256
            if string[i + 2] == '\x02':
                index += ord(string[i + 3]);
            colors.append(input_colors[index])
            i += 4
        return colors

    def __encode_colors_id(self, graph):
        """ Encode a string where an integer is encoded over four bytes.
            The even ones contain either '\x01' if the following value is null
            or '\x02'. The odd ones contain a dummy value if it should be null,
            or the actual value """
        string = []
        for c in graph:
            if c / 256 == '\x00':
                string.append('\x01')
                string.append('\x01')
            else:
                string.append('\x02')
                string.append(chr(c / 256))

            if c % 256 == 0:
                string.append('\x01')
                string.append('\x01')
            else:
                string.append('\x02')
                string.append(chr(c % 256))
        return "".join(string)

    def __distance(self, c1, c2):
        return pow(c1[0] - c2[0], 2)    \
                + pow(c1[1] - c2[1], 2) \
                + pow(c1[2] - c2[2], 2)

    def color_reducer(self, colors, threshold):
        """ The argument must be a list of colors defined in base LAB.
            The output result contains the maximal number of colors of
            the provided list where each color is at at least a distane
            threshold from the others. """
        graph = []
        for i1, c1 in enumerate(colors):
            for i2, c2 in enumerate(colors):
                if c1 != c2 and self.__distance(c1, c2) > threshold:
                    graph.extend([i1, i2])

        in_string = c_char_p(self.__encode_colors_id(graph))
        out_string = c_char_p('\x00' * (len(colors) * 4 + 1))
        number_color_in = c_uint(len(graph) / 2)

        self.lib.color_reducer(in_string, number_color_in, out_string)

        result = self.__decode_colors_id(out_string.value, colors)

        return result

