from . import base
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
from colormath.color_objects import LabColor, sRGBColor
import networkx as nx
import networkx.algorithms.shortest_paths.generic as algorithms


class Reducer(base.Filter):
    threshold = 20

    @staticmethod
    def distance(c_1, c_2):
        """
        Returns the CIEDE2000 distance of the two provided colors.

        :arg c_1: a tuple representing an hsl color
        :arg c_2: a tuple representing an hsl color
        :see: `<https://en.wikipedia.org/wiki/Color_difference/>`_
        """
        rgb1 = sRGBColor(c_1[0], c_1[1], c_1[2])
        rgb2 = sRGBColor(c_2[0], c_2[1], c_2[2])
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

        :arg palette: the input palette
        :return: the output palette
        :rtype: an instance of :class:`hapycolor.palette.Palette`
        """
        reduced_colors = Reducer.reduce(palette.colors)
        palette.colors = reduced_colors
        return palette

    @staticmethod
    def reduce(colors):
        global_graph = Reducer.generate_graph(colors)
        assert len(global_graph) == len(colors)
        graphs = Reducer.find_subgraphs(global_graph)
        reduced_colors = []
        for graph in graphs:
            inverted_graph = nx.Graph()
            inverted_graph.add_edges_from(nx.non_edges(graph))
            reduced_graph = Reducer.get_maximum_clique(inverted_graph)
            if not reduced_graph:
                reduced_colors.append(list(graph.nodes)[0])
            else:
                reduced_colors.extend(reduced_graph)
        return reduced_colors

    @staticmethod
    def generate_graph(colors):
        """
        For each couple of colors, a node is created and if two colors are "too
        close", they will be set as neighbours.

        :arg colors: A list of rgb tuples.
        :return: A hash table which maps every color to a :class:Node
        """
        graph = nx.Graph()
        for c in colors:
            graph.add_node(c)

        for i, c_1 in enumerate(colors[:-1]):
            for c_2 in colors[i+1:]:
                if Reducer.distance(c_1, c_2) < Reducer.threshold:
                    graph.add_edge(c_1, c_2)
        return graph

    @staticmethod
    def find_subgraphs(graph):
        """
        Given a list of nodes (color and neighbours), this function finds all
        the connected subgraphs. In other words, it creates K disjoint subsets
        (graphs) where for each couple of nodes of a graph, it exists a path
        that connects them. Furthermore, given two nodes of two differents
        subsets, there are no paths connecting them.
        """
        subgraphs = []

        while graph:
            connected = []
            graph_iter = iter(graph)
            n_1 = next(graph_iter)
            connected.append(n_1)
            for n_2 in graph_iter:
                if algorithms.has_path(graph, n_1, n_2):
                    connected.append(n_2)
            for node in connected:
                graph.remove_node(node)
            subgraphs.append(Reducer.generate_graph(connected))
        return subgraphs

    def get_maximum_clique(graph):
        """
        Computes the maximal clique of a provided graph. The generated graphs'
        nodes correspond to the colors and for each couple of colors which are
        sufficiently far apart, there is an edge. The distance used is the
        CIEDE2000 distance and when this value is larger than the provided
        threshold, the colors are considered sufficently appart.

        To improve the performances of the algorithm, if the graph contains
        more than 60 colors, it will be reduced to this value.

        :arg graph: A hash table mapping a color to a :class:Node. It
            In order to optimize the algorithm, only connected graphs should be
            provided.
        :arg threshold: The minimal LAB distance between two colors.
        :see: :func:`Reducer.distance`
        :see: `<https://en.wikipedia.org/wiki/Color_difference/>`_
        """
        # if len(graph) <= 1:
        #     return [n.color for n in graph]

        # if len(graph) > 60:
        #     graph = graph[:60]

        cliques = list(nx.find_cliques(graph))
        if not cliques:
            return []
        return max(cliques, key=len)
