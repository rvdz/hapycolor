import unittest
from  unittest import mock
from hapycolor.filters.reducer import Reducer
import subprocess as sp
import networkx as nx
from networkx import convert_node_labels_to_integers as cnlti
from hapycolor import palette as pltte


class TestReducer(unittest.TestCase):
    @mock.patch("hapycolor.filters.reducer.Reducer.threshold", 20)
    def test_reducer_taipei(self):
        """
        When debuging the reduction filter, it is highly advised to uncomment
        the prints of this test, as it precisely shows its effects.

        The following colors have been exported from "taipei" image, located
        in the image folder of this project. The goal is to analyse accurately
        the effects of the reduction algorithm and when setting a threshold
        for the algorithm.
        """
        from hapycolor import visual
        colors = [(83, 7, 53), (13, 25, 84), (18, 22, 81), (19, 28, 91),
                  (24, 26, 88), (56, 7, 70), (46, 19, 76), (40, 25, 87),
                  (56, 27, 88), (11, 46, 81), (22, 39, 89), (46, 38, 88),
                  (22, 29, 97), (22, 20, 112), (44, 14, 113), (11, 40, 100),
                  (19, 37, 101), (10, 55, 103), (20, 54, 110), (45, 45, 105),
                  (81, 16, 73), (75, 36, 89), (114, 43, 78), (85, 25, 102),
                  (86, 39, 101), (16, 78, 110), (152, 36, 55), (141, 40, 88),
                  (173, 45, 89), (144, 47, 101), (175, 52, 101), (205, 50, 91),
                  (229, 39, 90), (205, 58, 102), (241, 55, 105), (225, 94, 94),
                  (212, 73, 108), (231, 72, 105), (248, 72, 106), (251, 87, 108),
                  (241, 79, 114), (252, 90, 116), (252, 102, 108), (247, 116, 108),
                  (254, 103, 117), (254, 119, 119), (22, 144, 115), (47, 230, 117),
                  (82, 244, 120), (103, 232, 117), (183, 171, 92), (234, 159, 93),
                  (254, 134, 120), (252, 145, 113), (159, 241, 112), (252, 246, 88),
                  (252, 207, 115), (228, 225, 100), (251, 241, 112), (35, 35, 145),
                  (19, 84, 137), (19, 107, 143), (32, 104, 158), (75, 76, 185),
                  (225, 91, 137), (248, 115, 134), (31, 159, 155), (86, 168, 155),
                  (33, 225, 157), (45, 240, 144), (79, 247, 138), (33, 165, 207),
                  (84, 163, 209), (42, 238, 211), (35, 217, 224), (41, 253, 250),
                  (49, 245, 242), (86, 236, 231), (250, 142, 135), (233, 160, 161),
                  (147, 236, 151), (253, 209, 138), (244, 233, 168), (158, 241, 217)]

        graph = None
        with mock.patch("hapycolor.filters.reducer.Reducer.threshold", 20):
            graph = Reducer.generate_graph(colors)
        self.assertEqual(len(colors), len(graph))
        graphs = Reducer.find_subgraphs(graph)
        self.assertEqual(len(graphs), 12)

        reduced_graphs = []
        # print()
        for graph in graphs:
            inverted_graph = nx.Graph()
            inverted_graph.add_edges_from(nx.non_edges(graph))
            reduced_graphs.append(Reducer.get_maximum_clique(inverted_graph))
            # visual.print_palette(list(graph.nodes))
            # visual.print_palette(reduced_graphs[-1])
            # print()
        self.assertEqual(sum([len(l) for l in reduced_graphs]), 24)

    @mock.patch("hapycolor.filters.reducer.Reducer.threshold", 30)
    def test_generate_graph(self):
        colors = [(100, 0, 0), (90, 0, 0), (110, 0, 0),
                  (0, 100, 0), (0, 110, 0), (0, 90, 0),
                  (0, 0, 100), (0, 0, 90), (0, 0, 110)]

        expected = {(0, 0, 110): {(0, 0, 90): {}, (0, 0, 100): {}},
                    (0, 0, 100): {(0, 0, 110): {}, (0, 0, 90): {}},
                    (0, 0, 90): {(0, 0, 110): {}, (0, 0, 100): {}},
                    (0, 110, 0): {(0, 90, 0): {}, (0, 100, 0): {}},
                    (0, 100, 0): {(0, 90, 0): {}, (0, 110, 0): {}},
                    (0, 90, 0): {(0, 110, 0): {}, (0, 100, 0): {}},
                    (90, 0, 0): {(110, 0, 0): {}, (100, 0, 0): {}},
                    (100, 0, 0): {(110, 0, 0): {}, (90, 0, 0): {}},
                    (110, 0, 0): {(90, 0, 0): {}, (100, 0, 0): {}}}

        graph = Reducer.generate_graph(colors)
        self.assertDictEqual(dict(graph.adj), expected)

    def test_get_maximum_clique_0_colors(self):
        graph = nx.Graph()
        result = Reducer.get_maximum_clique(graph)
        self.assertEqual(result, [])

    def test_get_maximum_clique_2_colors(self):
        graph = nx.Graph()
        graph.add_edge((100, 0, 0), (101, 0, 0))
        result = Reducer.get_maximum_clique(graph)
        expected = {(100, 0, 0), (101, 0, 0)}
        self.assertSetEqual(set(result), expected)

    def test_apply_14_colors(self):
        colors = [(239, 106, 135), (42, 240, 236), (53, 217, 115),
                  (89, 240, 119), (92, 234, 150), (167, 220, 106),
                  (216, 79, 104), (43, 227, 146), (217, 54, 100),
                  (246, 81, 111), (71, 203, 214), (166, 73, 99),
                  (195, 64, 175), (49, 49, 159)]

        expected = {(166, 73, 99), (239, 106, 135), (217, 54, 100),
                    (42, 240, 236), (89, 240, 119), (43, 227, 146),
                    (167, 220, 106), (71, 203, 214), (195, 64, 175),
                    (49, 49, 159)}

        palette = pltte.Palette()
        palette.colors = colors
        with mock.patch("hapycolor.filters.reducer.Reducer.threshold", 10):
            result = Reducer.apply(palette)
        self.assertSetEqual(set(result.colors), expected)

    def test_threshold_0(self):
        values = [(12, 13, 14), (24, 25, 26), (100, 101, 102)]
        expected = {(12, 13, 14), (24, 25, 26), (100, 101, 102)}
        with mock.patch("hapycolor.filters.reducer.Reducer.threshold", 0):
            result = Reducer.reduce(values)
        self.assertSetEqual(set(result), expected)


    def test_reduce_15_integers(self):
        values = [1, 2, 3, 6, 7, 8, 11, 12, 13, 16, 17, 18, 21, 22, 23]
        expected = {1, 8, 11, 16, 21}

        with mock.patch("hapycolor.filters.reducer.Reducer.threshold", 3), \
                mock.patch("hapycolor.filters.reducer.Reducer.distance",
                           TestReducer.mock_distance):
            result = Reducer.reduce(values)
        result.sort()
        self.assertIn(result[0], [1, 2, 3])
        self.assertIn(result[1], [6, 7, 8])
        self.assertIn(result[2], [11, 12, 13])
        self.assertIn(result[3], [16, 17, 18])
        self.assertIn(result[4], [21, 22, 23])

    def test_find_subgraphs(self):
        """
        Asserts that the function
        :func:hapycolor.filters.reducer.Reducer.find_subgraphs returns two
        connected graphs (n0, n1, n2, n3, n4,n 5) and (n6, n7) when provided
        with the following graph:

         n0   n6
        |  |  |
        n1 n2 n7
        |  |
        n3 n4
           |
           n5
        """
        graph = nx.Graph()
        graph.add_edges_from([(0, 1), (1, 3), (0, 2), (2, 4), (4, 5), (6, 7)])
        expected = [nx.Graph([(0, 1), (1, 3), (0, 2), (2, 4), (4, 5)]),
                    nx.Graph([(6, 7)])]

        with mock.patch("hapycolor.filters.reducer.Reducer.distance",
                        TestReducer.mock_distance):
            graphs = Reducer.find_subgraphs(graph)

        for graph, exp in zip(graphs, expected):
            self.assertEqual(graph.nodes, exp.nodes)

    @staticmethod
    def mock_distance(value_1, value_2):
        return abs(value_1 - value_2)

    @mock.patch("hapycolor.filters.reducer.Reducer.distance", mock_distance)
    @mock.patch("hapycolor.filters.reducer.Reducer.threshold", 3)
    def test_graph_reduction(self):
        colors = [0, 1, 2, 3, 6, 7, 8, 11, 12, 13, 14, 16]
        expected = [{0, 1, 2, 3}, {6, 7, 8}, {11, 12, 13, 14, 16}]
        graphs = Reducer.find_subgraphs(Reducer.generate_graph(colors))
        for exp, graph in zip(expected, graphs):
            self.assertSetEqual(exp, set(graph.nodes))
