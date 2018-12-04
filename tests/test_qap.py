import unittest
from hapycolor.targets.vim.qap import QAP, Node
from hapycolor import helpers

class TestQAP(unittest.TestCase):
    def test_distance(self):
        val = [((50, 0.2, 0.5), (100, 0.2, 0.5), 50),
               ((0, 0.2, 0.5), (100, 0.2, 0.5), 100),
               ((359, 0.2, 0.5), (1, 0.2, 0.5), 2),
               ((0, 0.2, 0.5), (359, 0.2, 0.5), 1)]
        for (c_1, c_2, expected) in val:
            self.assertEqual(Node.distance(c_1, c_2), expected)

    def test_one_values(self):
        freq = [0.3]
        colors = [helpers.rgb_to_hsl(c) for c in [(20, 40, 50)]]
        qap = QAP(colors, freq)
        self.assertEqual(qap(), list(zip(colors, freq)))

    def test_two_values(self):
        freq = [0.3, 0.7]
        colors = [helpers.rgb_to_hsl(c) for c in [(15, 17, 20), (20, 40, 50)]]
        qap = QAP(colors, freq)
        self.assertEqual(qap(), list(zip(colors, freq)))

    def test_on_high_freq(self):
        freq = [0.15, 0.7, 0.15]
        # Red, Orange, Blue => most frequent color (0.7) should be assigned to blue
        colors = [helpers.rgb_to_hsl(c) for c in [(255, 0, 0), (255, 129, 0), (0, 102, 204)]]
        qap = QAP(colors, freq)
        expected = (colors[2], 0.7)
        self.assertIn(expected, qap())

    def test_size_four(self):
        freq = [0.1, 0.4, 0.4, 0.1]
        # Red, Orange, Blue, Green
        rgb_colors = [(255, 0, 0), (255, 129, 0), (0, 102, 204), (0, 153, 0)]
        colors = [helpers.rgb_to_hsl(c) for c in rgb_colors]
        qap = QAP(colors, freq)
        res = qap()

        expected_1 = (colors[2], 0.4)
        self.assertIn(expected_1, res)
        expected_2 = (colors[3], 0.4)
        self.assertIn(expected_2, res)

    def test_size_four_frequencies_mixed(self):
        freq = [0.4, 0.1, 0.4, 0.1]
        # Red, Orange, Blue, Green
        rgb_colors = [(255, 0, 0), (255, 129, 0), (0, 102, 204), (0, 153, 0)]
        colors = [helpers.rgb_to_hsl(c) for c in rgb_colors]
        qap = QAP(colors, freq)
        res = qap()

        expected_1 = (colors[2], 0.4)
        self.assertIn(expected_1, res)
        expected_2 = (colors[3], 0.4)
        self.assertIn(expected_2, res)

    def test_size_four_colors_mixed(self):
        freq = [0.1, 0.4, 0.4, 0.1]
        # Green, Orange, Blue, Red
        rgb_colors = [(0, 153, 0), (255, 129, 0), (0, 102, 204), (255, 0, 0)]
        colors = [helpers.rgb_to_hsl(c) for c in rgb_colors]
        res = QAP(colors, freq)()

        expected_1 = (colors[0], 0.4)
        self.assertIn(expected_1, res)
        expected_2 = (colors[2], 0.4)
        self.assertIn(expected_2, res)
