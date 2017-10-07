from colormath.color_diff import delta_e_cie2000
from colormath.color_objects import LabColor, HSLColor
from colormath.color_conversions import convert_color
from platform import system
from ctypes import cdll, c_uint, c_wchar_p
import utils
import os

class ColorReducer():

    def __init__(self):
        # TODO: Should not depend on the directory from where the python script is called
        # Generate a shared object of the algorithm
        os.system("make")

        # Library defining a maximal clique algorithm
        if system() == "Darwin":
            self.lib = cdll.LoadLibrary("./libcolor_reducer.dylib")
        else:
            self.lib = cdll.LoadLibrary("./libcolor_reducer.so")

    def __distance(self, c1, c2):
        """ The employed distance between colors is the CIEDE2000
            @see https://en.wikipedia.org/wiki/Color_difference """
        hsl1 = HSLColor(c1[0], c1[1], c1[2])
        hsl2 = HSLColor(c2[0], c2[1], c2[2])
        lab1 = convert_color(hsl1, LabColor)
        lab2 = convert_color(hsl2, LabColor)
        return delta_e_cie2000(lab1, lab2)

    def color_reducer(self, colors, threshold):
        """ The argument must be a list of colors defined in base HSL.
            The output result contains the maximal number of colors of
            the provided list where each color is at at least a distane
            threshold from the others. """

        # TODO: Fixup when only one color is given
        if len(colors) == 1:
            return colors

        colors_set = list(set(colors))
        graph = []
        for i1, c1 in enumerate(colors_set):
            for i2, c2 in enumerate(colors_set):
                if c1 != c2 and self.__distance(c1, c2) > threshold:
                    assert(i1 < len(colors_set) and i2 < len(colors_set))
                    graph.extend([i1, i2])

        in_string = c_wchar_p(self.__encode_colors_id(graph))
        out_string = c_wchar_p('\x00' * (len(colors_set) * 2 + 1))
        number_color_in = c_uint(len(graph) // 2)

        self.lib.color_reducer(in_string, number_color_in, out_string)

        return [colors_set[i] for i in self.__decode_colors_id(out_string.value)]

    def __decode_colors_id(self, string):
        """ Subtract one in order to get the original values of the color identifiers """
        return [ord(e) - 1 for e in string]

    def __encode_colors_id(self, graph):
        """ Add one to the ids in order to avoid the problem of the null character which
            breaks the python string """
        return "".join([chr(c + 1) for c in graph])
