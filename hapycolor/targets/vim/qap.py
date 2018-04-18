from copy import deepcopy
import math

class Node:
    def __init__(self, qap, parent=None, state=[]):
        self.qap = qap
        self.parent = parent
        self.state = state
        self.generator = self._child_gen()

    def _child_gen(self):
        for c in [c for c in self.qap.colors if c not in self.state]:
            state = deepcopy(self.state) + [c]
            yield Node(self.qap, self, state)

    def next_child(self):
        return next(self.generator, None)

    def is_leaf(self):
        return len(self.state) == len(self.qap.colors)

    def distance(c1, c2):
        max_hue = 360
        return abs(c1[0] - c2[0]) if abs(c1[0] - c2[0]) < max_hue // 2 \
                else max_hue - abs(c1[0] - c2[0])

    def compute_value(self):
        value = 0
        vertices = [(self.qap.frequencies[i], c) for (i, c) in enumerate(self.state)]
        for f_i, c_i in vertices:
            for f_j, c_j in vertices:
                if c_i != c_j:
                    value += Node.distance(c_i, c_j) / (f_i * f_j)
        return value

    def __repr__(self):
        return '<Node state="{}">'.format(self.state)


class QAP:
    def __init__(self, colors, frequencies):
        self.colors = colors
        self.frequencies = frequencies

        root_node = Node(self)
        self.nodes = [root_node]

        self._is_end = False
        self.results = []
        self.bounds = math.inf

    def run(self):
        while not self.is_end():
            node = self.get_last_node()

            if node.is_leaf():
                self.remove_node(node)
                self.add_result(node)
                continue

            if not self.satisfy_bounds(node):
                self.remove_node(node)
                continue

            child = node.next_child()
            if child is None:
                self.remove_node(node)
            else:
                self.add_node(child)
        return [(c, self.frequencies[i]) for i, c in enumerate(self.results)]

    def satisfy_bounds(self, node):
        return node.compute_value() < self.bounds

    def get_last_node(self):
        if self.nodes:
            return self.nodes[-1]

    def add_node(self, node):
        self.nodes.append(node)

    def remove_node(self, node):
        if node in self.nodes:
            self.nodes.remove(node)
        if not self.nodes:
            self._is_end = True

    def is_end(self):
        return self._is_end

    def check_end(self):
        self._is_end = len(self.nodes) == 0

    def add_result(self, node):
        value = node.compute_value()
        if  value < self.bounds:
            self.results = node.state
            self.bounds = value

    def get_bounds(self):
        return deepcopy(self.bounds)
