from hapycolor import exceptions
import numpy as np



class PAM:
    """
    Partition Around Medoids

        The goal of the algorithm is to minimize the average dissimilarity of
        objects to their closest selected object.
        A k-medoid algorithm was chosen instead of a regular k-means, since it
        is often useful to have a color representing a cluster of colors that
        is also contained in the picture. The algorithm is divided in two
        steps: the build phase, and the swap phase.

    Build

        A collection of k objects are selected for an initial set S

    Swap

        The second phase, SWAP, attempts to improve the the set of selected
        object :math:`selected` and, therefore, to improve the quality of the
        clustering. This is done by considering all pairs :math:`(i, h)` where
        :math:`i` in :math:`selected` and :math:`h` in :math:`unselected` and
        consists of computing the effect :math:`T_{ih}` on the sum of
        dissimilarities between objects and the closest selected object caused
        by swapping :math:`i` and :math:`h`, that is, by transferring :math:`i`
        from :math:`selected` to :math:`unselected` and transferring :math:`h`
        from :math:`unselected` to :math:`selected`. The computation of
        :math:`T_{ih}` involves the computation of the contribution
        :math:`K_{jih}` of each object :math:`j \in unselected − {h}` to the
        swap of :math:`i` and :math:`h`. Note that we have either
        :math:`d(j, i) > D_j` or :math:`d(j, i) = D_j`.
    """
    def __init__(self, colors, K, distance):
        if K > len(colors):
            msg = "Impossible to classify the provided palette into {} \
classes, since it only has {} colors.".format(K, len(colors))
            raise exceptions.PAMException(msg)

        self.colors = colors
        self.K = K
        self.selected = []
        self.unselected = self.colors[:]
        self.distance = distance

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
                distance_c.append(self.distance(c, s))
            medoid_index = distance_c.index(min(distance_c))
            medoid = self.selected[medoid_index]
            if medoid in clusters:
                clusters[medoid].append(c)
            else:
                clusters[medoid] = [c]
        return clusters

    def _build(self):
        # Initialize `selected` by adding to it an object for which the sum
        # of the distances to all other objects is minimal.

        distances = {}
        for c_1 in self.colors:
            distances[c_1] = []
            for c_2 in self.colors:
                distances[c_1].append(self.distance(c_1, c_2))

        mean_distances = [np.array(distances[key]).mean()
                          for key in distances]
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
                        d_j_i = self.distance(i, j)
                        g_i += max(D_j - d_j_i, 0)
                g.append((i, g_i))
            # Choose that object i that maximizes g_i
            max_i = max(g, key=lambda _: _[1])[0]
            self.selected.append(max_i)
            del self.unselected[self.unselected.index(max_i)]

    def _swap(self):
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
                d_j_i = self.distance(j, i)
                D_j = self._d_p(j)
                d_j_h = self.distance(j, h)
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
        dist = map(lambda c: self.distance(p, c), self.selected)
        return min(list(dist))

    def _e_p(self, p):
        """
        the dissimilarity between `p` and the second closest object in
        `self.selected`.
        """
        dist = list(map(lambda c: self.distance(c, p), self.selected))
        dist.sort()
        if len(dist) > 1:
            return dist[1]
        else:
            return dist[0]

