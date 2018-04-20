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
    """
    QAP
    ===

    Introduction
    ------------
    The goal of the Quadratic Assignment Problem (QAP) is to assign `n`
    facilities to `n` locations in such a way as to minimize the assignment
    cost. The assignment cost is the sum, over all pairs, of the flow between
    a pair of facilities multiplied by the distance between their assigned
    locations.

    Formal definition
    -----------------
    The quadratic assignment problem is as follows:
    Given two sets, P ("facilities") and L ("locations"), of equal size,
    together with a weight function :math:`w : P × P \rightarrow \mathbb{R}`
    and a distance function :math:`d : L × L \rightarrow \mathbb{R}`. Find
    the bijection :math:`f : P \rightarrow L` ("assignment") such that the cost
    function:

    .. math::
        \sum_{a,b \in P} w_{a,b}d_{f(a),f(b)}

    How it is used in Hapycolor
    ---------------------------
    In this project, one example of the uses of this algorithm is the
    following: when exporting the generated palette to `vim`, the colors
    are first classified into k groups, but then, needs to be assigned to
    one of vim's syntax groups. To do so, clever way would be to assign
    the colors that are far appart to very frequent syntactic groups.
    In other words, the objective is to maximize the distance of the colors
    assigned to the syntactic groups that appear the most in a program's code.

    How to use it
    -------------
    This class takes two arguments: the colors and the weights, e.g when
    exporting to vim, they represent the frequencies of the different
    syntactic groups. Then the implemented algorithm solves the problem
    by exploring the different possible combination following a Branch and
    Bound pattern. Eventually, it will return a list of tuples
    `(color, frequency)`.

    .. note:: this implementation currently uses the colors' hues
        difference as the distance between colors. Maybe it could
        be interesting trying with the CIE delta distance.

    .. see:: https://en.wikipedia.org/wiki/Branch_and_bound

    .. see:: https://en.wikipedia.org/wiki/Quadratic_assignment_problem
    """
    def __init__(self, colors, frequencies):
        self.colors = colors
        self.frequencies = frequencies

        root_node = Node(self)
        self.nodes = [root_node]

        self._is_end = False
        self.results = []
        self.bounds = math.inf

    def __call__(self):
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
