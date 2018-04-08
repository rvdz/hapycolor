from hapycolor import targets
from hapycolor import helpers
from hapycolor import exceptions
from hapycolor import palette as pltte
from hapycolor.targets.vim_environment import VimEnvironments
from . import eight_bit_colors
from . import base


class Vim(base.Target):
    """
    Generates a colorscheme with the provided palette. This colorscheme will
    be named 'hapycolor' and will be located in the directory provided when
    initializing the target.

    Currently, it supports 8bit and 24bit terminals, but by default, vim only
    supports 8bit colors. To enable 24bit support, the option 'set
    termguicolor', available since Vim 7.4, should be set in your vimrc.

    .. todo:: Check if the option was introduced with Vim 7.4

    """
    exclusive_groups = [
             ["Comment"],
             ["Search"],
             ["String"],
            ]

    groups = [
              ["Boolean"],
              ["Character"],
              ["Keyword"],
              ["Number", "Float"],
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
             ]

    configuration_key = "colorscheme_vim"

    def is_config_initialized():
        try:
            return Vim.configuration_key in Vim.load_config()
        except exceptions.InvalidConfigKeyError:
            return False

    def initialize_config():
        """
        Creates the path where the colorscheme will be generated, and stores it
        in the project's configuration file.
        """
        if not VimEnvironments.is_vim_installed():
            print("Vim is not installed, this target will be disabled. Once"
                  + "  you install vim, ")
            return

        p = None
        try:
            p = VimEnvironments.bundle_plugins_path()
        except exceptions.NoCommonPathFound:
            p = Vim.custom_path()

        p = p / "hapycolor" / "colors"
        if not p.exists():
            p.mkdir(parents=True)
        Vim.save_config({Vim.configuration_key: (p / "hapycolor.vim").as_posix()})

    def custom_path():
        p = helpers.input_path("Path to vim's custom plugins directory: ")
        if not p.is_absolute():
            p = p.resolve()

        if not p.is_dir():
            raise exceptions.WrongInputError("Must be a directory")

    def compatible_os():
        return [targets.OS.LINUX, targets.OS.DARWIN]

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
let g:colors_name = "Hapycolor"'''
        f.write(header + "\n\n")

    @staticmethod
    def __print_base(fg, bg, f):
        Vim.__write_entry(f, "Normal", fg, bg)
        Vim.__write_entry(f, "NonText", fg, bg)

    @staticmethod
    def __write_entry(f, category, fg, bg=None):
        entry = ["hi " + category,
                 "guifg=" + helpers.rgb_to_hex(fg),
                 "ctermfg=" + str(eight_bit_colors.rgb2short(fg))]

        if bg is not None:
            entry.extend(["guibg=" + helpers.rgb_to_hex(bg),
                          "ctermbg=" + str(eight_bit_colors.rgb2short(bg))])

        elements = 3 if bg is None else 5
        f.write(("{: <20} " * elements + "\n").format(*entry))

    @staticmethod
    def __print_visual(fg, bg, f):
        """ TODO: alter fg and bg, maybe use a color instead of fg """
        fg = (170, 170, 170)
        bg = (34, 34, 34)
        Vim.__write_entry(f, "Visual", fg, bg)

    @staticmethod
    def __print_body(color_manager, f):
        for i, G in enumerate(Vim.exclusive_groups):
            color = color_manager.get_next_color()
            color_manager.remove_last()
            for g in G:
                Vim.__write_entry(f, g, color)

        for i, G in enumerate(Vim.groups):
            color = color_manager.get_next_color()
            for g in G:
                Vim.__write_entry(f, g, color)


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
        self.current = 0
        self.size = len(rgb_colors)
        self.removed = []

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

    def remove_last(self):
        self.removed.append(self.current)

    def get_next_color(self):
        """
        Considering a sequence of incrementing indexes, this function will
        return the first color of each label. Once all the labels' first
        values have been returned, it retrives the seconds and so on.
        Once all the colors will been used, it repeates the pattern.
        """
        while self.current in self.removed:
            self.current = (self.current + 1) % self.size

        label = self.current % len(self.colors)
        while len(self.colors[label]) == 0:
            label = (label + 1) % len(self.colors)
        i = (self.current // len(self.colors)) % len(self.colors[label])
        self.current = (self.current + 1) % self.size
        return helpers.hsl_to_rgb(self.colors[label][i])
