import enum
import datetime
from . import base
from . import eight_bit_colors
from . import vim_helpers
from hapycolor import targets
from hapycolor import exceptions
from hapycolor import helpers


class Lightline(base.Target):
    """
    Overview:

    A lightline theme is defined by a template which uses the following
    undeclared variables:

    - Yellow
    - Green
    - Blue
    - Red
    - Magenta
    - Orange
    - Foreground
    - Background

    Then, once a palette is fed to the class, a lightline colorscheme is
    generated by pairing the variables to colors defined in the provided
    palette.

    Supported themes:

    - Landscape
    - One
    - Wombat
    """

    _themes = ["landscape.vim", "one.vim", "wombat.vim", "solarized.vim"]
    ThemeEnum = enum.Enum("ThemeEnum",
                          [(t.split('.')[0].upper(),
                            "hapycolor/targets/lightline_themes/" + t)
                           for t in _themes])

    # The colorscheme's path
    colorscheme_key = "colorscheme"

    plugin_name = "lightline.vim"

    # Will be asked during target's configuration
    theme_key = "theme"

    def initialize_config():
        colorscheme_path = Lightline.select_colorscheme_path()
        theme = Lightline.select_theme()
        Lightline.save_config({
                               Lightline.colorscheme_key: colorscheme_path,
                               Lightline.theme_key: str(theme.value)
                              })

    def reconfigure():
        try:
            entry = int(input("\nTheme: 1\nLightline's path: 2\nEntry: "))
            if entry not in [1, 2]:
                raise ValueError
        except ValueError:
            print("Wrong input")
            Lightline.reconfigure()

        if entry == 1:
            theme = Lightline.select_theme()
            Lightline.save_config({Lightline.theme_key: str(theme.value)})
        elif entry == 2:
            colorscheme_path = Lightline.select_colorscheme_path()
            Lightline.save_config({Lightline.colorscheme_key: colorscheme_path})

    def select_colorscheme_path():
        p = vim_helpers.VimHelpers.find_plugin(Lightline.plugin_name)
        file_path = (p / "autoload/lightline/colorscheme/hapycolor.vim")
        return file_path.expanduser().as_posix()

    def select_theme():
        try:
            print("\nSelect a theme:")
            for i, t in enumerate(Lightline.ThemeEnum):
                print(t.name + ": (" + str(i) + ")")
            theme_i = int(input("Theme: "))
            if theme_i < 0 or len(Lightline.ThemeEnum) <= theme_i:
                raise ValueError
            return list(Lightline.ThemeEnum)[theme_i]
        except ValueError:
            print("Value must be an integer between 0 and "
                  + str(len(Lightline.ThemeEnum)))
            return Lightline.select_theme()

    def is_config_initialized():
        try:
            config = Lightline.load_config()
            return (Lightline.colorscheme_key in config) \
                and (Lightline.theme_key in config)
        except exceptions.InvalidConfigKeyError:
            return False

    def compatible_os():
        return [targets.OS.DARWIN, targets.OS.LINUX]

    def export(palette, image_path):
        """
        This function extract the targeted colors of the palette and defines
        the color's variables used in the theme's template defined in the
        configuration file.
        """
        colorscheme = Lightline.load_config()[Lightline.colorscheme_key]
        with open(colorscheme, 'w') as f:
            f.write(Lightline.header(image_path))

            # Defines input palette's variables
            colors = Lightline.get_colors(palette)
            f.write(Lightline.set_variable("foreground", palette.foreground))
            f.write("\n")
            f.write(Lightline.set_variable("background", palette.background))
            f.write("\n")

            for label in colors:
                f.write(Lightline.set_variable(label, colors[label]) + "\n")
            f.write("\n")

            body_path = Lightline.load_config()[Lightline.theme_key]
            with open(body_path, "r") as body_file:
                f.write(body_file.read())
            f.write("\n")

            f.write(Lightline.footer())

    def footer():
        return "let g:lightline#colorscheme#hapycolor#palette \
            = lightline#colorscheme#flatten(s:p)"

    def header(image_path):
        now = datetime.datetime.now()
        date = "%s/%s/%s %s:%s:%s." % (now.day, now.month, now.year, now.hour,
                                       now.minute, now.second)
        return """
" =============================================================================
" Filename: autoload/lightline/colorscheme/hapycolor.vim
" Author: hapycolor
" License: MIT License
" Last Change: %s
" Source image: %s
" =============================================================================
""" % (date, image_path)

    def get_colors(palette):
        """
        For each label defined in the color enumeration, affects a color of
        the palette.
        """
        lcm = ColorManager(palette.colors)
        colors = {}
        for e in ColorEnum:
            colors[e.name.lower()] = lcm.get(e)
        return colors

    def set_variable(label, color):
        return "let s:" + label + " = [ '" + helpers.rgb_to_hex(color) + "', "\
            + str(eight_bit_colors.rgb2short(color)) + "]"


class ColorEnum(enum.Enum):
    __order__ = 'RED ORANGE YELLOW GREEN BLUE MAGENTA'
    RED     = [345, 15]
    ORANGE  = [16, 32]
    YELLOW  = [33, 74]
    GREEN   = [75, 166]
    BLUE    = [167, 255]
    MAGENTA = [256, 344]

    def get_label(hue):
        for e in ColorEnum:
            if e.value[0] <= hue and hue <= e.value[1]:
                return e
        return ColorEnum.RED

    def get_next(label):
        enums = [l for l in ColorEnum]
        i = enums.index(label)
        return enums[(i+1) % len(enums)]


class ColorManager:
    """
    For each variable needed by the theme, defines a dictionary which binds
    a the enumerate to a value of the palette's colors.

    .. todo:: Apply another reduction filter? Since we need only a few colors,
        it makes sense.
    """
    def __init__(self, colors):
        if not all([helpers.can_be_rgb(c) for c in colors]):
            raise exceptions.ColorFormatError("Must be a list of rgb colors")

        # Classify the colors according to their hue
        sorted_colors = {}
        for c in [helpers.rgb_to_hsl(col) for col in colors]:
            label = ColorEnum.get_label(c[0])
            if label in sorted_colors:
                sorted_colors[label].append(c)
            else:
                sorted_colors[label] = [c]

        self.labels = {}
        for label in ColorEnum:
            original_label = label
            while sorted_colors.get(label) is None:
                label = ColorEnum.get_next(label)
            # Get color whose saturation is max
            colors = sorted_colors[label]
            # If there is only one color in this label and another label uses
            # this list of colors, it will fail.
            # color = colors.pop(colors.index(max(colors, key=lambda c: c[1])))
            color = max(colors, key=lambda c: c[1])
            self.labels[original_label] = color

    def get(self, label):
        return helpers.hsl_to_rgb(self.labels[label])
