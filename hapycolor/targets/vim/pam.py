from hapycolor import exceptions
import numpy as np
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
from colormath.color_objects import LabColor, sRGBColor

class PAM:
    """
    Partition Around Medoids algorithm
    The goal of the algorithm is to minimize the average dissimilarity of
    objects to their closest selected object
    """
    def __init__(self, palette, K):
        if K > len(palette.colors):
            msg = "Impossible to classify the provided palette into {} " \
                    + "classes, since it only has {} colors."
            raise exceptions.PAMException(msg)

        self.colors = [PAM.rgb_to_lab(c) for c in palette.colors]
        PAM.distances = self._evaluate_distances()
        self.K = K
        self.selected = []
        self.unselected = self.colors[:]

    @staticmethod
    def rgb_to_lab(c):
        rgb = sRGBColor(c[0], c[1], c[2])
        return convert_color(rgb2, LabColor)

    @staticmethod
    def lab_to_rgb(c):
        return convert_color(rgb2, sRGBColor)

    def __call__(self):
        """
        Performs the PAM algorithm on the provided colors and returns a
        dictionary that pairs each cluster's medoid with the colors classified
        as belonging to them.
        """
        self._build()
        self._swap()
        clusters = {}

        for c in self.colors:
            distance_c = []
            for s in self.selected:
                distance_c.append(PAM.distance(c, s))
            medoid_index = distance_c.index(min(distance_c))
            medoid = PAM.lab_to_rgb(self.selected[medoid_index])
            if medoid in clusters:
                clusters[medoid].append(PAM.lab_to_rgb(c))
            else:
                clusters[medoid] = [PAM.lab_to_rgb(c)]
        return clusters

    def _build(self):
        """
        A collection of k objects are selected for an initial set S
        """

        # Initialize `selected` by adding to it an object for which the sum
        # of the distances to all other objects is minimal.
        mean_distances = [np.array(dist).mean() for dist in PAM.distances]
        min_index = mean_distances.index(min(mean_distances))
        self.selected.append(self.colors[min_index])
        del self.unselected[min_index]

        for _ in range(self.K - 1):
            g = []
            # Consider an object i in `unselected` as a candidate for inclusion
            # into the set of selected objects
            for i in self.unselected:
                g_i = 0
                # For an object j in `unselected` − {i}. Compute D_j, the
                # dissimilarity between j and the closest object in S
                for j in self.unselected:
                    if i != j:
                        D_j = self._d_p(j)
                        d_j_i = PAM.distance(i, j)
                        g_i += max(D_j - d_j_i, 0)
                g.append((i, g_i))
            # Choose that object i that maximizes g_i
            max_i = max(g, key=lambda _: _[1])[0]
            self.selected.append(max_i)
            del self.unselected[self.unselected.index(max_i)]

    def _swap(self):
        """
        The second phase, SWAP, attempts to improve the the set of selected
        object `selected` and, therefore, to improve the quality of the
        clustering. This is done by considering all pairs `(i, h)` where `i`
        in `selected` and `h` in `unselected` and consists of computing
        the effect `T_i_h` on the sum of dissimilarities between objects
        and the closest selected object caused by swapping `i` and `h`,
        that is,  by transferring `i` from `selected` to `unselected` and
        transferring `h` from `unselected` to `selected`. The computation
        of `T_i_h` involves the computation of the contribution `K_j_i_h`
        of each object `j` in `unselected − {h}` to the swap of `i`and `h`.
        Note that we have either `d(j, i) > D_j` or `d(j, i) = D_j`.
        """
        T = -1
        while T < 0 and self.unselected:
            swaps = [(i, h) for i in self.selected for h in self.unselected]
            contributions = []
            for i, h in swaps:
                T_i_h = self._swap_i_h(i, h)
                contributions.append(((i, h), T_i_h))

            (i, h), T = min(contributions, key=lambda _: _[1])
            if T < 0:
                del self.selected[self.selected.index(i)]
                del self.unselected[self.unselected.index(h)]
                self.unselected.append(i)
                self.selected.append(h)

    def _swap_i_h(self, i, h):
        T_i_h = 0
        for j in self.unselected:
            if h != j:
                d_j_i = PAM.distance(j, i)
                D_j = self._d_p(j)
                d_j_h = PAM.distance(j, h)
                if d_j_i > D_j:
                    K_j_i_h = min(d_j_h - D_j, 0)
                elif d_j_i == D_j:
                    E_j = self._e_p(j)
                    K_j_i_h = min(d_j_h, E_j) - D_j
                T_i_h += K_j_i_h
        return T_i_h


    def _d_p(self, p):
        """
        The dissimilarity between `p` and the closest object in `self.selected`
        """
        dist = map(lambda c: PAM.distance(p, c), self.selected)
        return min(list(dist))

    def _e_p(self, p):
        """
        the dissimilarity between `p` and the second closest object in
        `self.selected`.
        """
        dist = list(map(lambda c: PAM.distance(c, p), self.selected))
        dist.sort()
        if len(dist) > 1:
            return dist[1]
        else:
            return dist[0]

    def distance(c1, c2):
        """
        Returns the CIEDE2000 distance of the two provided colors.

        :arg c1: a tuple representing a Lab color
        :arg c2: a tuple representing a Lab color
        :see: `<https://en.wikipedia.org/wiki/Color_difference/>`_
        """
        return delta_e_cie2000(lab1, lab2)

    def _evaluate_distances(self):
        distances = {}
        for c_1 in self.colors:
            for c_2 in self.colors:
                if c_1 in distances:
                    distances[c_1][c_2] = PAM.distance(c_1, c_2)
                else:
                    distances[c_1] = {c_2: PAM.distance(c_1, c_2)}
        return distances
