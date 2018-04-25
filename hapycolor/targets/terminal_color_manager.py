"""
Terminal module
"""

from hapycolor import exceptions
from hapycolor import helpers
from hapycolor.targets import pam


class Terminal():
    SIMPLE_SORT = True
    """
    For more details about standard and high-intensity terminal colors, see:
    `Standard and Hight-intensity colors
    <https://en.wikipedia.org/wiki/ANSI_escape_code#8-bit>`_

    Initializes a :class:`Terminal`'s instance with a list of colors.

    :arg colors: a `list` of rgb colors
    """
    def __init__(self, colors):
        if colors.__class__ != list:
            msg = "'colors' must be a list of colors"
            raise exceptions.WrongInputError(msg)
        if not all([helpers.can_be_rgb(c) for c in colors]):
            msg = "'colors' must be defined in the rgb base"
            raise exceptions.ColorFormatError(msg)
        if len(colors) < 6:
            msg = "a minimum of six colors is required"
            raise exceptions.InvalidPaletteException(msg)

        colors = Terminal._classify_hue(colors)
        assert len(colors) == 6
        medoids = Terminal._classify_luminosity(colors)
        assert len(medoids) == 6

        if Terminal.SIMPLE_SORT:
            self.colors = Terminal._simple_sort(medoids)
        else:
            self.colors = Terminal._sort(medoids)
        assert len(self.colors) == 16


    def cast(self, i):
        assert 0 <= i < 16, "i: {}".format(i)
        return self.colors[i]

    @staticmethod
    def _classify_hue(colors):
        """
        Breaks the palette's colors into six clusters according to their hues,
        since there are 8 colors in a terminal's palette (plus 8 light colors),
        but two are reserved for black and white.
        """
        k = 6

        def hue_diff(c1, c2):
            return abs(c1[0] - c2[0])
        hsl_colors = [helpers.rgb_to_hsl(c) for c in colors]
        return pam.PAM(hsl_colors, k, hue_diff)()

    @staticmethod
    def _classify_luminosity(colors):
        """
        For each cluster created previously, divide by two each group according
        to their luminosity, and return the two medoids sorted by their
        luminosity.
        """
        def luminosity_diff(c1, c2):
            return abs(c1[2] - c2[2])

        medoids = []
        for medoid in colors:
            # Check if there is only one color in the cluster
            try:
                hue_split_cluster = pam.PAM(colors[medoid], 2, luminosity_diff)()
            except exceptions.PAMException:
                hue_split_cluster = [medoid] * 2
            c_1, c_2 = tuple([m for m in hue_split_cluster])
            normal, light = (c_1, c_2) if c_1[2] < c_2[2] else (c_2, c_1)
            medoids.append((normal, light))
        return medoids

    @staticmethod
    def _simple_sort(medoids):
        """
        Adds default values for the blacks and whites and adds fills the
        palette with the provided pairs (normal/bright) of colors.

        :see: `Standard and High-intensity colors
            <https://en.wikipedia.org/wiki/ANSI_escape_code#8-bit>`_
        """
        colors = [None] * 16

        # Black
        colors[0] = (0, 0, 0)
        colors[8] = (0, 0, 0.3)
        # White
        colors[7] = (0, 0, 0.7)
        colors[15] = (0, 0, 1)
        # Others
        for i in range(1, 7):
            colors[i] = medoids[i-3][0]
        for i in range(9, 15):
            colors[i] = medoids[i-11][1]

        return [helpers.hsl_to_rgb(c) for c in colors]

    @staticmethod
    def _sort(medoids):
        """
        Does the same thing as the :func:`_simple_sort`, but also checks
        if a pair of colors belongs to the red's or green's hue
        interval. If not, defines default green or red components and
        initialize an array mapping each profile's ANSI value to a
        colors.

        :see: `Standard and High-intensity colors
            <https://en.wikipedia.org/wiki/ANSI_escape_code#8-bit>`_
        """
        green_component = None
        red_component = None
        other_components = []
        for (normal, light) in medoids:
            if (normal[0] < 25 or normal[0] > 345) and red_component is None:
                red_component = (normal, light)
            elif normal[0] < 160 and normal[0] > 60 \
                    and green_component is None:
                green_component = (normal, light)
            else:
                other_components.append((normal, light))

        if green_component is None:
            green_component = [(140, 1, 0.3), (120, 1, 0.7)]
        if red_component is None:
            red_component = [(0, 1, 0.45), (0, 1, 0.75)]

        colors = [None] * 16

        # Red
        colors[1] = red_component[0]
        colors[9] = red_component[1]
        # Green
        colors[2] = green_component[0]
        colors[10] = green_component[1]
        # Black
        colors[0] = (0, 0, 0)
        colors[8] = (0, 0, 0.3)
        # White
        colors[7] = (0, 0, 0.7)
        colors[15] = (0, 0, 1)
        # Others
        for i in range(3, 7):
            colors[i] = other_components[i-3][0]
        for i in range(11, 15):
            colors[i] = other_components[i-11][1]

        return [helpers.hsl_to_rgb(c) for c in colors]
