from hapycolor import helpers
from hapycolor import exceptions


class Palette:
    """ A palette is defined by rgb tuples stored in three attributes:

        - foreground
        - background
        - colors: an unordered list of colors. Cannot be empty
     """

    def __init__(self):
        self._foreground = None
        self._background = None
        self._colors = None
        self.current = None
        self.other = {}

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

    @property
    def hexcolors(self):
        return (helpers.rgb_to_hex(self.foreground),
                helpers.rgb_to_hex(self.background),
                [helpers.rgb_to_hex(c) for c in self.colors])

    @colors.setter
    def colors(self, rgb_colors):
        if not isinstance(rgb_colors, list) or not rgb_colors \
                or not all([helpers.can_be_rgb(c) for c in rgb_colors]):
            raise exceptions.ColorFormatError("The color must be defined"
                                              + " in the rgb base")
        self._colors = rgb_colors

    def to_json(self, file_name):
        data = {
                "foreground": self.foreground,
                "background": self.background,
                "colors": self.colors
               }
        print("Saving palette to: ", file_name)
        helpers.save_json(file_name, data)

    def from_json(json_file):
        json_palette = helpers.load_json(json_file)
        if "foreground" not in json_palette or \
                "background" not in json_palette or \
                "colors" not in json_palette:
            msg = "ERROR: The provided json file does not implement a valid" \
                    + " palette."
            raise exceptions.PaletteFormatError(msg)

        palette = Palette()
        palette.foreground = tuple(json_palette["foreground"])
        palette.background = tuple(json_palette["background"])
        palette.colors = [tuple(c) for c in json_palette["colors"]]
        return palette

    def __iter__(self):
        self.current = 0
        return self

    def __next__(self):
        color = self._colors[self.current % len(self._colors)]
        self.current += 1
        return color

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
