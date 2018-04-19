from hapycolor import targets
from hapycolor import helpers
from hapycolor import exceptions
from hapycolor import palette as pltte
from hapycolor.targets import eight_bit_colors
from hapycolor.targets import base
from hapycolor.targets.vim.environment import VimEnvironments
from hapycolor.targets.vim.pam import PAM


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
    groups = [
              ["Comment"],
              ["Constant", "String", "Character", "Number", "Boolean", "Float"],
              ["Identifier", "Function"],
              ["Statement", "Conditional", "Repeat", "Label", "Operator",
               "Keyword", "Exception"],
              ["PreProc", "Include", "Define", "Macro", "PreCondit"],
              ["Type", "StorageClass", "Structure", "Typedef"],
              ["Special", "SpecialChar", "Tag", "Delimiter", "SpecialComment",
               "Debug"],
              ["Underlined"],
              # ["Ignore"], ["Error"], ["Todo"],
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
        entry = {Vim.configuration_key: (p / "hapycolor.vim").as_posix()}
        Vim.save_config(entry)

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

        vcm = VimColorManager(palette.colors, len(Vim.groups))

        with open(Vim.load_config()[Vim.configuration_key], "w+") as f:
            Vim.__print_header(f)
            Vim.__print_base(palette.foreground, palette.background, f)
            Vim.__print_visual(palette.foreground, palette.background, f)
            Vim.__print_body(vcm, f)

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
        for i, minor_groups in enumerate(Vim.groups):
            colors = color_manager.cast(i, len(minor_groups))
            for (group, color) in zip(minor_groups, colors):
                Vim.__write_entry(f, group, color)


class VimColorManager:
    """ Manages vim's color's distribution """
    def __init__(self, rgb_colors, number_groups):
        if rgb_colors.__class__ != list or len(rgb_colors) == 0 \
                or not all([helpers.can_be_rgb(c) for c in rgb_colors]):
            msg = "The colors must be defined in the rgb base"
            raise exceptions.ColorFormatError(msg)

        dict_colors = PAM(rgb_colors, number_groups)()
        self.colors = [dict_colors[cluster] for cluster in dict_colors]

    def cast(self, group_id, group_length):
        cluster_size = len(self.colors[group_id])
        return [self.colors[group_id][i % cluster_size]
                for i in range(group_length)]
