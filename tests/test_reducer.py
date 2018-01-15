import unittest
from hapycolor.filters.reducer import Reducer


class TestReducer(unittest.TestCase):
    def test_reducer_valid_entry(self):
        colors = [(239, 106, 135), (42, 240, 236), (53, 217, 115),
                  (89, 240, 119), (92, 234, 150), (167, 220, 106),
                  (216, 79, 104), (43, 227, 146), (217, 54, 100),
                  (246, 81, 111), (71, 203, 214), (166, 73, 99),
                  (195, 64, 175), (49, 49, 159)]

        threshold = 10

        possible_expected_outputs = [[0, 1, 3, 5, 7, 8, 10, 11, 12, 13],
                                     [0, 1, 3, 5, 6, 7, 10, 11, 12, 13],
                                     [1, 3, 5, 7, 8, 9, 10, 11, 12, 13]]

        edges = Reducer.get_edges(colors, threshold)
        maximum_clique = Reducer.get_maximum_clique(edges)
        maximum_clique.sort()

        self.assertIn(maximum_clique, possible_expected_outputs)
