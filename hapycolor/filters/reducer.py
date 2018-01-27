from . import base
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
from colormath.color_objects import LabColor, sRGBColor
import networkx as nx


class Node:
    def __init__(self, color):
        self.color = color
        self.neighbours = []

    def add_neighbour(self, other):
        self.neighbours.append(other)


class Reducer(base.Filter):
    threshold = 20

    @staticmethod
    def distance(c1, c2):
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
        This distance is currently a constant integer which defines the minimal
        `CIEL2000 <https://en.wikipedia.org/wiki/Color_difference>`_ distance
        between colors.

        :param palette: the input palette
        :return: the output palette
        :rtype: an instance of :class:`Palette`
        """
        nodes = Reducer.gen_graphs(palette.colors)
        graphs = Reducer.find_subgraphs(nodes)
        reduced_colors = []
        for g in graphs:
            reduced_graph = Reducer.get_maximum_clique(g, Reducer.threshold)
            reduced_colors.extend(reduced_graph)
        palette.colors = reduced_colors
        return palette

    def gen_graphs(colors):
        nodes = {}
        for c in colors:
            nodes[c] = Node(c)

        for i1, c1 in enumerate(colors):
            for i2, c2 in enumerate(colors):
                if c1 != c2 and Reducer.distance(c1, c2) < Reducer.threshold:
                    nodes[c1].add_neighbour(nodes[c2])
                    nodes[c2].add_neighbour(nodes[c1])
        return nodes

    @staticmethod
    def find_neighbours(node, graph):
        for n in node.neighbours:
            if n.color not in graph:
                graph[n.color] = n
                Reducer.find_neighbours(n, graph)
        return graph

    def find_subgraphs(nodes):
        graphs = []
        while nodes:
            root_k = next(iter(nodes))
            root = nodes[root_k]
            graph = Reducer.find_neighbours(root, {root.color: root})
            for n in graph:
                del nodes[n]
            graphs.append(list(graph.values()))
        return graphs

    def get_maximum_clique(graph, threshold):
        """
        Computes the maximal clique of a provided graph. The generated graphs'
        nodes correspond to the colors and for each couple of colors which are
        sufficiently far apart, there is an edge. The distance used is the
        CIEDE2000 distance and when this value is larger than the provided
        threshold, the colors are considered sufficently appart.

        To improve the performances of the algorithm, if the graph contains
        more than 60 colors, it will be reduced to this value.

        .. see:: :func:Reducer.distance()
        """
        if len(graph) <= 1:
            return [n.color for n in graph]

        if len(graph) > 60:
            graph = graph[:60]

        edges = []
        for i1, c1 in enumerate(graph):
            for i2, c2 in enumerate(graph):
                dist = Reducer.distance(c1.color, c2.color)
                if i1 != i2 and dist >= threshold:
                    edges.append((i1, i2))
        cliques = list(nx.find_cliques(nx.Graph(data=edges)))
        if len(cliques) == 0:
            return []
        max_clique = max(cliques, key=lambda c: len(c))
        return [graph[i].color for i in max_clique]
