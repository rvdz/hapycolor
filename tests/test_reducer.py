import unittest
from unittest.mock import patch
from hapycolor.filters.reducer import Reducer, Node
import subprocess as sp


class TestReducer(unittest.TestCase):
    @patch("hapycolor.filters.reducer.Reducer.threshold", 20)
    def test_reducer_taipei(self):
        """
        When debuging the reduction filter, it is highly advised to uncomment
        the prints of this test, as it precisely shows its effects.

        The following colors have been exported from "taipei" image, located
        in the image folder of this project. The goal is to analyse accurately
        the effects of the reduction algorithm and when setting a threshold
        for the algorithm.
        """
        # from hapycolor import visual
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

        nodes = Reducer.generate_nodes(colors)
        self.assertEqual(len(colors), len(nodes))
        graphs = Reducer.find_subgraphs(nodes)
        reduced_graphs = []
        # print()
        for g in graphs:
            reduced_graphs.append(Reducer.get_maximum_clique(g, 20))
            # visual.print_palette([n.color for n in g])
            # visual.print_palette(reduced_graphs[-1])
            # print()
        self.assertEqual(len(graphs), 12)
        self.assertEqual(sum([len(l) for l in reduced_graphs]), 26)

    def test_reducer_valid_entry(self):
        colors = [(239, 106, 135), (42, 240, 236), (53, 217, 115),
                  (89, 240, 119), (92, 234, 150), (167, 220, 106),
                  (216, 79, 104), (43, 227, 146), (217, 54, 100),
                  (246, 81, 111), (71, 203, 214), (166, 73, 99),
                  (195, 64, 175), (49, 49, 159)]

        expected_output = [(166, 73, 99), (239, 106, 135), (216, 79, 104),
                           (42, 240, 236), (89, 240, 119), (43, 227, 146),
                           (167, 220, 106), (71, 203, 214), (195, 64, 175),
                           (49, 49, 159)]

        nodes = Reducer.generate_nodes(colors)
        graphs = Reducer.find_subgraphs(nodes)
        reduced_colors = []
        threshold = 10

        for g in graphs:
            reduced_colors.extend(Reducer.get_maximum_clique(g, threshold))
        self.assertEqual(set(expected_output), set(reduced_colors))

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
        n0 = Node(0)
        n1 = Node(1)
        n2 = Node(2)
        n0.add_neighbour(n1)
        n1.add_neighbour(n0)
        n0.add_neighbour(n2)
        n2.add_neighbour(n0)
        n3 = Node(3)
        n1.add_neighbour(n3)
        n3.add_neighbour(n1)
        n4 = Node(4)
        n2.add_neighbour(n4)
        n4.add_neighbour(n2)
        n5 = Node(5)
        n4.add_neighbour(n5)
        n5.add_neighbour(n4)
        n6 = Node(6)
        n7 = Node(7)
        n6.add_neighbour(n7)
        n7.add_neighbour(n6)

        nodes = {n0.color: n0, n1.color: n1, n2.color: n2, n3.color: n3,
                 n4.color: n4, n5.color: n5, n6.color: n6, n7.color: n7}

        graphs = Reducer.find_subgraphs(nodes)
        graphs_id = []
        for g in graphs:
            graphs_id.append([n.color for n in g])
        graphs_set = [tuple(sorted(lst)) for lst in graphs_id]
        expected_graphs = [tuple(range(6)), (6, 7)]

        self.assertEqual(set(graphs_set), set(expected_graphs))

    def mock_distance(v1, v2):
        return abs(v1 - v2)

    @patch("hapycolor.filters.reducer.Reducer.distance", mock_distance)
    @patch("hapycolor.filters.reducer.Reducer.threshold", 3)
    def test_graph_reduction(self):
        colors = [0, 1, 2, 3, 6, 7, 8, 11, 12, 13, 14, 16]
        expected_graphs = [[0, 1, 2, 3], [6, 7, 8], [11, 12, 13, 14, 16]]
        graphs = Reducer.find_subgraphs(Reducer.generate_nodes(colors))
        for i, g in enumerate(graphs):
            self.assertEqual(set(expected_graphs[i]),
                             set([n.color for n in g]))
