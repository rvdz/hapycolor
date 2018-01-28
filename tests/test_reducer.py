import unittest
from unittest.mock import patch
from hapycolor.filters.reducer import Reducer, Node
import subprocess as sp


class TestReducer(unittest.TestCase):
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

        nodes = Reducer.gen_graphs(colors)
        graphs = Reducer.find_subgraphs(nodes)
        reduced_colors = []
        threshold = 10

        for g in graphs:
            reduced_colors.extend(Reducer.get_maximum_clique(g, threshold))
        self.assertEqual(set(expected_output), set(reduced_colors))

    @unittest.skip("Still developing, might never be finished")
    def test_cpp(self):
        proc = sp.run("cd ./hapycolor/filters/reducer/ && make test",
                      shell=True, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
        if proc.returncode != 0:
            self.fail("C++ reducer tests failed, for more details, run: cd"
                      + "  ./hapycolor/filters/reducer/ && make test")

    def test_find_subgraphs(self):
        """
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
        graphs = Reducer.find_subgraphs(Reducer.gen_graphs(colors))
        for i, g in enumerate(graphs):
            self.assertEqual(set(expected_graphs[i]),
                             set([n.color for n in g]))
