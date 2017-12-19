from colormath.color_diff import delta_e_cie2000
from colormath.color_conversions import convert_color
from colormath.color_objects import LabColor, sRGBColor
import networkx as nx

from hapycolor import helpers
from hapycolor import config
from hapycolor import exceptions
from . import base


class Reducer(base.Filter):

    threshold = 15

    @staticmethod
    def __distance(c1, c2):
        """
        Returns the CIEDE2000 distance of the two provided colors.
        `see <https://en.wikipedia.org/wiki/Color_difference/>`_

        :arg c1: a tuple representing an hsl color
        :arg c2: a tuple representing an hsl color
        """
        rgb1 = sRGBColor(c1[0], c1[1], c1[2])
        rgb2 = sRGBColor(c2[0], c2[1], c2[2])
        lab1 = convert_color(rgb1, LabColor)
        lab2 = convert_color(rgb2, LabColor)
        return delta_e_cie2000(lab1, lab2)

    @staticmethod
    def apply(palette):
        """
        Returns a reduced list of rgb colors. The output result contains the
        maximal number of colors of the provided list, where each color is at
        at least a distance threshold from the others.

        arg: colors: a list of colors defined in base RGB
        arg: threshold: a positive integer defining the minimal `CIEL2000
        <https://en.wikipedia.org/wiki/Color_difference>`_ distance between
        colors.
        """
        edges = Reducer.get_edges(palette.colors, Reducer.threshold)
        maximum_clique = Reducer.get_maximum_clique(edges)
        palette.colors = [palette.colors[i] for i in maximum_clique]
        return palette

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
