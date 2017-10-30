from colormath.color_diff import delta_e_cie2000
from colormath.color_conversions import convert_color
from colormath.color_objects import LabColor, HSLColor
from ctypes import c_uint, c_wchar_p

from hapycolor import helpers
from hapycolor import config
from hapycolor import exceptions

class Reducer():

    def __init__(self):
        """ Compiling if necessary and loading the library defining a maximal
            clique algorithm """
        self.lib = config.get_reduce_library()

    def __distance(self, c1, c2):
        """ The employed distance between colors is the CIEDE2000
            @see https://en.wikipedia.org/wiki/Color_difference """
        hsl1 = HSLColor(c1[0], c1[1], c1[2])
        hsl2 = HSLColor(c2[0], c2[1], c2[2])
        lab1 = convert_color(hsl1, LabColor)
        lab2 = convert_color(hsl2, LabColor)
        return delta_e_cie2000(lab1, lab2)

    def reduce(self, colors, threshold):
        """ The argument must be a list of colors defined in base HSL.
            The output result contains the maximal number of colors of
            the provided list where each color is at at least a distane
            threshold from the others. """

        if colors.__class__ != list or len(colors) == 0:
            raise exceptions.ReducerArgumentsError("'colors' must be a list of at least one hsl color")
        if not all([helpers.can_be_hsl(c) for c in colors]):
            raise exceptions.ColorFormatError("'colors' must be a list of hsl colors")

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

        # Would be better to create a list of \x00 so that only the portion of the list filled by the reducer
        # algorithm would be decoded, but because c_wchar_p('\x00') fails on some versions of python3.5
        # that cannot be done and the decoded list contains duplicates
        out_string = c_wchar_p('\x01' * (len(colors_set) * 2 + 1))
        number_color_in = c_uint(len(graph) // 2)

        self.lib.reduce(in_string, number_color_in, out_string)

        return list(set([colors_set[i] for i in self.__decode_colors_id(out_string.value)]))

    def __decode_colors_id(self, string):
        """ Subtract one in order to get the original values of the color identifiers """
        return [ord(e) - 1 for e in string]

    def __encode_colors_id(self, graph):
        """ Add one to the ids in order to avoid the problem of the null character which
            breaks the python string """
        return "".join([chr(c + 1) for c in graph])
