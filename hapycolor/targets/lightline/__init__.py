"""
Lightline module
"""
import enum
import datetime
from pathlib import Path

from hapycolor import targets
from hapycolor import exceptions
from hapycolor import helpers
from hapycolor.targets import base
from hapycolor.targets import eight_bit_colors
from hapycolor.targets import vim
from hapycolor.targets import pam


class Lightline(base.Target):
    """
    Replaces the following tokens defined in a given template by colors
    generated from the input image:

    - $FG
    - $BG
    - $NORMAL
    - $INSERT
    - $REPLACE
    - $VISUAL

    Basically, it splits evenly the hues into four groups and maps the medoids
    of each clusters to a mode.

    This version of hapycolor prefers using templates instead of letting the
    user directly provide a configuration file since some effort is required
    in order to understand how the configuration interacts with the end result.
    So, it seemed more interesting to use templates that already define specific
    the variables to be replaced with the generated colors. If a user wants to
    add his own templates, this can be done just by adding the file with a '
    vim' extension into `./hapycolor/targets/lightline/`.

    Currently supported themes:

    - Landscape
    - One
    - Wombat
    - Solarized
    """
    # The colorscheme's path
    colorscheme_key = "colorscheme"

    # Will be asked during target's configuration
    theme_key = "theme"

    @staticmethod
    def initialize_config():
        colorscheme_path = Lightline.select_colorscheme_path()
        theme = Lightline.select_theme()
        Lightline.save_config({
            Lightline.colorscheme_key: colorscheme_path,
            Lightline.theme_key: str(theme.value)})

    @staticmethod
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
            entry = {Lightline.colorscheme_key: colorscheme_path}
            Lightline.save_config(entry)

    @staticmethod
    def select_colorscheme_path():
        p = vim.environment.VimEnvironments.find_plugin("lightline.vim")
        file_path = p + "/autoload/lightline/colorscheme/hapycolor.vim"
        return file_path

    @staticmethod
    def select_theme():
        module_dir = Path(__file__).parent
        ThemeEnum = enum.Enum("ThemeEnum",
                              [(t.stem.upper(), module_dir / t)
                               for t in module_dir.iterdir() if ".vim" == t.suffix])
        try:
            print("\nSelect a theme:")
            for i, theme in enumerate(ThemeEnum):
                print(theme.name + ": (" + str(i) + ")")
            theme_i = int(input("Theme: "))
            if theme_i < 0 or len(ThemeEnum) <= theme_i:
                raise ValueError
            return list(ThemeEnum)[theme_i]
        except ValueError:
            print("Value must be an integer between 0 and "
                  + str(len(ThemeEnum)))
            return Lightline.select_theme()

    @staticmethod
    def is_config_initialized():
        try:
            config = Lightline.load_config()
            return (Lightline.colorscheme_key in config) \
                and (Lightline.theme_key in config)
        except exceptions.InvalidConfigKeyError:
            return False

    @staticmethod
    def compatible_os():
        return [targets.OS.DARWIN, targets.OS.LINUX]

    @staticmethod
    def export(palette, image_path):
        """
        This function extract the targeted colors of the palette and defines
        the color's variables used in the theme's template defined in the
        configuration file.
        """

        theme = [Lightline.add_header(image_path)]
        theme.extend(Lightline.add_body())
        theme = Lightline.add_colors(theme, palette)

        colorscheme = Lightline.load_config()[Lightline.colorscheme_key]
        with open(colorscheme, 'w') as colorscheme_file:
            colorscheme_file.write('\n'.join(theme))

    @staticmethod
    def add_body():
        theme_path = Lightline.load_config()[Lightline.theme_key]
        body = []
        with open(theme_path, "r") as theme_file:
            body = theme_file.read().splitlines()
        return body

    @staticmethod
    def add_colors(theme, palette):
        """
        Splits the palette evenly into four clusters of hues and pairs
        the medoid of each one with the following modes:
        'NORMAL', 'INSERT', 'REPLACE', 'VISUAL', 'FOREGROUND', 'BACKGROUND'
        """
        colors = Lightline.classify(palette.colors)

        hsl_colors = [helpers.rgb_to_hsl(c) for c in colors]
        hsl_colors.sort(key=lambda c: c[0])
        hsl_colors = [hsl_colors[1], hsl_colors[0], hsl_colors[3], hsl_colors[2]]
        colors = [helpers.hsl_to_rgb(c) for c in hsl_colors]
        colors.extend([palette.foreground, palette.background])

        modes = ["$NORMAL", "$INSERT", "$REPLACE", "$VISUAL", "$FG", "$BG"]
        for mode, color in zip(modes, colors):
            new_value = "'{}', {}".format(helpers.rgb_to_hex(color),
                                          eight_bit_colors.rgb_to_short(color))
            theme = [line.replace(mode, new_value) for line in theme]
        return theme

    @staticmethod
    def classify(colors):
        def distance(c_1, c_2):
            """ Evaluates the hue's distance """
            return abs(c_1[0] - c_2[0])

        # There are four modes: Insert, Visual, Normal and Replace
        k = 4
        colors = pam.PAM(colors, k, distance)()

        # Only the medoids of each cluster will used
        return [m for m in colors]

    @staticmethod
    def add_header(image_path):
        now = datetime.datetime.now()
        date = "{}/{}/{} {}:{}:{}.".format(now.day, now.month, now.year,
                                           now.hour, now.minute, now.second)
        return """
" =============================================================================
" Filename: autoload/lightline/colorscheme/hapycolor.vim
" Author: hapycolor
" License: MIT License
" Last Change: {}
" Source image: {}
" =============================================================================
""".format(date, image_path)
