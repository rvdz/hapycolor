Color Filters
=====================

.. contents::

.. _filter_label:

Filter
------
For instance, Hapycolor is able to determine if a color is too bright or too dark. A first step, would be to convert the
colors in an `hsl <https://en.wikipedia.org/wiki/HSL_and_HSV>`_ base and then add conditions on the luminosity. But that
would be an illusory solution, as a matter of fact, both hsl/hsv or rgb color bases do not match the human's eye perception
of colors. That is why, we handpicked more than a hundred colors that we consider being at the interface between the space
where the colors are too bright (respectively, too dark) and the space where they are not. From this discretisation, Hapycolor
is able to generate a more fine discretisation of this hyperplan which is used to filter the colors.
A similar approach has been implemented in order to filter out the colors that are deemed not enough saturated.

.. _reduction_label:

Reduction
---------
A second innovative concept embedded into Hapycolor's color processing core, is the ability to properly reduce the number
of colors. Indeed, one of the challenges is to remove the colors that are to close to one another from the human's eye
perspective, but still keeping the largest palette possible. Thus, supposing that such a color base exists, the problem
can be also stated as: imagining that each color represent a node in a graph and that two colors sufficiently "far" from each other,
have a common vertex. In this situation, the question becomes
"`what is the maximum clique? <https://en.wikipedia.org/wiki/Clique_problem#Finding_a_single_maximal_clique>`_",
an inquiry already answered by `Coenraad Bron <https://en.wikipedia.org/wiki/Coenraad_Bron>`_ and Joep Kerbosch with the
`Bron-Kerbosch algorithm <https://en.wikipedia.org/wiki/Bron%E2%80%93Kerbosch_algorithm>`_.

Back to the concreteness of our world, the hypothesis of the existence of a color base that is perceptually uniform still
needs to be proven, and worse, found, if one hopes to disclose the impenetrable mysteries of Ricing's Art. I am pleased
to announce another saviour: `Richard S. Hunter <https://en.wikipedia.org/wiki/Richard_S._Hunter>`_, a man and a color
scientist who invented the `Lab color space <https://en.wikipedia.org/wiki/Lab_color_space>`_ from which has been devised
by the `International Commission on Illumination <https://en.wikipedia.org/wiki/International_Commission_on_Illumination>`_
the `CIEL*a*b color space <https://en.wikipedia.org/wiki/CIELUV>`_. The commission crafted various distances that could
operate in this space, among others the: `CIEDE2000 <https://en.wikipedia.org/wiki/Color_difference#CIEDE2000>`_, that have
been used by Hapycolor to define the maximal clique problem.

.. _`add filters`:

How to add a color filter?
--------------------------
In order to add a custom filter, a class inheriting from :class:`hapycolor.filters.base.Filter` should be implemented in the filters module.
Its main method, "apply" takes in a :class:`hapycolor.Palette` and should output another :class:`hapycolor.Palette`.
In addition, in order to enable it, the module's name should be added in the "Filters" section of the configuration file,
coupled with a value representing the complexity of the algorithm. At runtime, hapycolor searches for classes stored in
the provided modules that inherits from :class:`hapycolor.filters.base.Filter` and whose name is a PascalCase version of the respective module
(which should be named in snake_case, but you already know that, I hope).

.. note:: Maybe, in a near future, this last constraint could be removed.
