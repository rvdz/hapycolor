from hapycolor import helpers
from hapycolor import exceptions


class Palette:
    """ A palette is defined by rgb tuples stored in three attributes:
        - foreground
        - background
        - colors: an unordered list of colors
         """

    def __init__(self):
        self._foreground = None
        self._background = None
        self._colors     = None

    @property
    def foreground(self):
        return self._foreground

    @foreground.setter
    def foreground(self, rgb_color):
        if not helpers.can_be_rgb(rgb_color):
            raise exceptions.ColorFormatError("The color must be defined"
                                              + " in the rgb base")
        self._foreground = rgb_color

    @property
    def background(self):
        return self._background

    @background.setter
    def background(self, rgb_color):
        if not helpers.can_be_rgb(rgb_color):
            raise exceptions.ColorFormatError("The color must be defined"
                                              + " in the rgb base")
        self._background = rgb_color

    @property
    def colors(self):
        return self._colors

    @colors.setter
    def colors(self, rgb_colors):
        if rgb_colors.__class__ != list or len(rgb_colors) == 0 \
                or not all([helpers.can_be_rgb(c) for c in rgb_colors]):
            raise exceptions.ColorFormatError("The color must be defined"
                                              + " in the rgb base")
        self._colors = rgb_colors

    def is_initialized(self):
        """ Returns 'True' if the palette has been correctly initialized,
            else 'False' """
        return (self._background.__class__ == tuple
                and helpers.can_be_rgb(self._background)
                and self._background.__class__ == tuple
                and helpers.can_be_rgb(self._background)
                and self._colors.__class__ == list
                and len(self._colors) != 0
                and all([helpers.can_be_rgb(c) for c in self._colors]))
