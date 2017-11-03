from colormath.color_diff import delta_e_cie2000
from colormath.color_conversions import convert_color
from colormath.color_objects import LabColor, sRGBColor
import networkx as nx

from hapycolor import helpers
from hapycolor import config
from hapycolor import exceptions


class Reducer():

    @staticmethod
    def __distance(c1, c2):
        """
        Returns the CIEDE2000 distance of the two provided colors.
        `see <https://en.wikipedia.org/wiki/Color_difference/>`_

        Keyword arguments:
        c1 -- a tuple representing an hsl color
        c2 -- a tuple representing an hsl color
        """
        rgb1 = sRGBColor(c1[0], c1[1], c1[2])
        rgb2 = sRGBColor(c2[0], c2[1], c2[2])
        lab1 = convert_color(rgb1, LabColor)
        lab2 = convert_color(rgb2, LabColor)
        return delta_e_cie2000(lab1, lab2)

    @staticmethod
    def apply(colors, threshold):
        """
        Returns a reduced list of rgb colors. The output result contains the
        maximal number of colors of the provided list, where each color is at
        at least a distance threshold from the others.

        Keyword arguments:
        colors -- a list of colors defined in base RGB
        threshold -- a positive integer defining the minimal `CIEL2000
        <https://en.wikipedia.org/wiki/Color_difference>`_ distance between
        colors.
        """
        if colors.__class__ != list or len(colors) == 0:
            msg = "'colors' must be a list of at least one rgn color"
            raise exceptions.ReducerArgumentsError(msg)
        if not all([helpers.can_be_rgb(c) for c in colors]):
            msg = "'colors' must be a list of rgb colors"
            raise exceptions.ColorFormatError(msg)

        # TODO: Fixup when only one color is given
        if len(colors) == 1:
            return colors

        in_colors_set = list(set(colors))

        edges = Reducer.get_edges(in_colors_set, threshold)
        maximum_clique = Reducer.get_maximum_clique(edges)
        return [in_colors_set[i] for i in maximum_clique]

    @staticmethod
    def get_edges(colors, threshold):
        for i1, c1 in enumerate(colors):
            for i2, c2 in enumerate(colors):
                if c1 != c2 and Reducer.__distance(c1, c2) > threshold:
                    assert(i1 < len(colors) and i2 < len(colors))
                    yield (i1, i2)

    @staticmethod
    def get_maximum_clique(edges):
        cliques = nx.find_cliques(nx.Graph(data=edges))
        return max(cliques, key=lambda c: len(c))
