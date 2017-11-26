from hapycolor import config
from hapycolor import helpers
from hapycolor import exceptions
from hapycolor import palette as pltte
from . import base


class Vim(base.Target):
    """
    Generates a colorscheme with the provided palette. This colorscheme will
    be named 'hapycolor' and will be located in the directory provided when
    initializing the target.

    Currently it only generates a colorscheme by setting 24bit colors, so it
    only works with versions of newer than Vim > 7.4 (TODO: To be confirmed)
    after enabling the option: 'set termguicolor'.
    """

    groups = [
              ["Comment"],
              ["Boolean"],
              ["Character"],
              ["Keyword"],
              ["Number"],
              ["String"],
              ["Float"],
              ["Conditional", "Repeat"],
              ["Include"],
              ["Macro"],
              ["Todo"],
              ["Constant"],
              ["Define"],
              ["Statement"],
              ["Cursor"],
              ["Delimiter"],
              ["Directory"],
              ["Structure"],
              ["Type"],
              ["Error", "ErrorMsg", "Exception"],
              ["PreCondit"],
              ["Function"],
              ["MatchParen"],
              ["Ignore"],
              ["Identifier"],
              ["Typedef"],
              ["Label"],
              ["Operator"],
              ["LineNr"],
              ["CursorLineNr"],
              ["CursorColumn"],
              ["Search"],
             ]

    configuration_key = "colorscheme_vim"

    def is_config_initialized():
        try:
            return Vim.configuration_key in Vim.load_config()
        except exceptions.InvalidConfigKeyError:
            return False

    def initialize_config():
        """
        Creates the path where the colorscheme will be generated, and stores it in
        the project's configuration file.
        """
        p = config.input_path("Path to vim's custom plugins directory: ")
        if not p.is_absolute():
            p = p.resolve()

        if not p.is_dir():
            raise exceptions.WrongInputError("Must be a directory")

        p = p / "hapycolor" / "colors"
        if not p.exists():
            p.mkdir(parents=True)
        Vim.save_config({Vim.configuration_key : (p / "hapycolor.vim").as_posix()})

    def compatible_os():
        return [config.OS.LINUX, config.OS.DARWIN]

    def export(palette, image_path):
        if palette.__class__ != pltte.Palette or not palette.is_initialized:
            msg = "The palette does not respect the appropriate structure"
            raise exceptions.PaletteFormatError(msg)

        with open(Vim.load_config()[Vim.configuration_key], "w+") as f:
            Vim.__print_header(f)
            Vim.__print_base(palette.foreground, palette.background, f)
            Vim.__print_visual(palette.foreground, palette.background, f)
            Vim.__print_body(VimColorManager(palette.colors), f)

    @staticmethod
    def __print_header(f):
        header = '''
set background=dark
if exists("syntax_on")
syntax reset
endif
let g:colors_name = "%s"''' % config.app_name()
        f.write(header + "\n\n")

    @staticmethod
    def __print_base(fg, bg, f):
        hex_fg = helpers.rgb_to_hex(fg)
        hex_bg = helpers.rgb_to_hex(bg)
        normal_entry = ["hi Normal", "guifg=" + hex_fg + "\tguibg=" + hex_bg + "\n"]
        f.write("{: <20}  {: <20}".format(*normal_entry))

        nontext_entry = ["hi NonText", "guifg=" + hex_fg + "\tguibg=" + hex_bg + "\n"]
        f.write("{: <20}  {: <20}".format(*nontext_entry))

    @staticmethod
    def __print_visual(fg, bg, f):
        """ TODO: alter fg and bg, maybe use a color instead of fg """
        # hex_fg = helpers.rgb_to_hex(fg)
        # hex_bg = helpers.rgb_to_hex(bg)
        hex_fg = "#AAAAAA"
        hex_bg = "#222222"
        line = ["hi Visual", "guifg=" + hex_fg + "\tguibg=" + hex_bg + "\n"]
        f.write("{: <20}  {: <20}".format(*line))

    @staticmethod
    def __print_body(vim_colors, f):
        for i, G in enumerate(Vim.groups):
            color = vim_colors.get_color(i)
            for g in G:
                line = ["hi " + g, "guifg=" + helpers.rgb_to_hex(color) + "\n"]
                f.write("{: <20}  {: <20}".format(*line))


class VimColorManager:
    """ Manages vim's color's distribution """
    def __init__(self, rgb_colors):
        if rgb_colors.__class__ != list or len(rgb_colors) == 0 \
                or not all([helpers.can_be_rgb(c) for c in rgb_colors]):
            msg = "The colors must be defined in the rgb base"
            raise exceptions.ColorFormatError(msg)
        self.labels = [[15+30*i, 15+30*(i+1)] for i in range(12)]
        self.labels.append([345, 15])       # Special case for red

        hsl_colors = [helpers.rgb_to_hsl(c) for c in rgb_colors]
        self.colors = self.__label_colors(hsl_colors)

    def __label_colors(self, colors):
        """ Sorts a list of hsl colors by labels """
        labeled_colors = [[] for k in range(12)]
        for col in colors:
            id_label = self.__find_label(col)
            labeled_colors[id_label].append(col)
        return labeled_colors

    def __find_label(self, hslcol):
        for i, l in enumerate(self.labels):
            if hslcol[0] >= l[0] and hslcol[0] < l[1]:
                return i
        return -1

    def get_color(self, index):
        """
        Considering a sequence of incrementing indexes, this function will
        return the first color of each label. Once all the labels' first
        values have been returned, it retrives the seconds and so on.
        Once all the colors will been used, it repeates the pattern.
        """
        label = index % len(self.colors)
        while len(self.colors[label]) == 0:
            label = (label + 1) % len(self.colors)
        i = (index // len(self.colors)) % len(self.colors[label])
        return helpers.hsl_to_rgb(self.colors[label][i])
