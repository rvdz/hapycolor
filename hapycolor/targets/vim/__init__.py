import json
from colormath.color_diff import delta_e_cie2000

from hapycolor import targets
from hapycolor import helpers
from hapycolor import exceptions
from hapycolor import palette as pltte
from hapycolor.targets import eight_bit_colors
from hapycolor.targets import base
from hapycolor.targets.vim.environment import VimEnvironments
from hapycolor.targets import pam
import hapycolor.targets.vim.qap


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

    # {Minor group title: [Minor group names]}
    groups = {
              "Comment": ["Comment"],
              "Constant": ["Constant", "String", "Character", "Number",
                           "Boolean", "Float"],
              "Identifier": ["Identifier", "Function"],
              "Statement": ["Statement", "Conditional", "Repeat", "Label",
                            "Operator", "Keyword", "Exception"],
              "PreProc": ["PreProc", "Include", "Define", "Macro",
                          "PreCondit"],
              "Type": ["Type", "StorageClass", "Structure", "Typedef"],
              "Special": ["Special", "SpecialChar", "Tag", "Delimiter",
                          "SpecialComment", "Debug"],
              # ["Underlined"],
              # ["Ignore"], ["Error"], ["Todo"],
             }

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

        color_manager = ColorManager(palette.colors)

        with open(Vim.load_config()[Vim.configuration_key], "w+") as f:
            Vim.__print_header(f)
            Vim.__print_base(palette.foreground, palette.background, f)
            Vim.__print_visual(palette.foreground, palette.background, f)
            Vim.__print_body(color_manager, f)

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
                 "ctermfg=" + str(eight_bit_colors.rgb_to_short(fg))]

        if bg is not None:
            entry.extend(["guibg=" + helpers.rgb_to_hex(bg),
                          "ctermbg=" + str(eight_bit_colors.rgb_to_short(bg))])

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
        for minor_group in Vim.groups:
            colors = color_manager.cast(minor_group)
            for (group, color) in zip(Vim.groups[minor_group], colors):
                Vim.__write_entry(f, group, color)


class ColorManager:
    """
    Manages vim's color's distribution

    Step 1

        Runs a clustering algorithm on the palette's colors and classifies
        them according to the number of major syntactic groups, i.e.:
        "Comment", "Constant", "Identifier", "Statement", "PreProc", "Type",
        "Special".

    Step 2

        The problem of casting the colors to the syntactic groups is a
        quadratic assignment problem. So, a QAP algorithm is ran with
        the medoids of the clusters previously found as the input colors,
        longside the occurrence frequencies, of each main syntactic group. The
        former elements represent the weights between two groups, for
        instance, the weight between the group "Comment" and the group
        "Statement" is the product of both their frequencies.
        Then, once the algorithms finishes, each syntactic group is assigned to
        a cluster, which will be retrieved by calling the method
        :func:`ColorManager.cast`.

    .. note::
        The occurrence frequencies are previously calculated and are located in
        `hapycolor/targets/vim/frequencies.json`

    .. note::
        If you are interested in correctly alter the occurrence frequencies
        of the syntactic groups, the vimscript
        `hapycolor/targets/vim/syntax_groups.vim` might be useful. It uses
        a list of files as the input, and generates a json file defining
        the occurrences of each syntactic group. Keep in mind that the
        result will be dependent on the syntax files and the active
        colorscheme file that you currently have. For instance, some
        does not define a specific color for minor syntactic groups and some
        do. Currently, this class aims at defining a cluster for each 'group'
        of syntactic groups, so it only defines frequences for the major
        groups.

    """
    def __init__(self, rgb_colors):
        if rgb_colors.__class__ != list or len(rgb_colors) == 0 \
                or not all([helpers.can_be_rgb(c) for c in rgb_colors]):
            msg = "The colors must be defined in the rgb base"
            raise exceptions.ColorFormatError(msg)

        def distance(c1, c2):
            return delta_e_cie2000(c1, c2)

        lab_colors = [helpers.rgb_to_lab(c) for c in rgb_colors]
        lab_classified = pam.PAM(lab_colors, len(Vim.groups), distance)()
        rgb_classified = {}
        for m in lab_classified:
            cluster = [helpers.lab_to_rgb(c) for c in lab_classified[m]]
            rgb_classified[helpers.lab_to_rgb(m)] = cluster

        self.groups_colors = ColorManager._pair_group_to_color(rgb_classified)

    def _pair_group_to_color(colors):
        medoids = [m for m in colors]
        groups_frequencies = ColorManager.load_frequencies()
        frequencies_groups = {v: k for k, v in groups_frequencies.items()}
        freq_values = [groups_frequencies[g]
                       for g in groups_frequencies]
        medoids_freqs = qap.QAP(medoids, freq_values)()
        groups_colors = {}
        for (m, freq) in medoids_freqs:
            groups_colors[frequencies_groups[freq]] = colors[m]
        return groups_colors

    def load_frequencies():
        frequencies_json = "hapycolor/targets/vim/frequencies.json"
        with open(frequencies_json, 'r') as f:
            frequencies = json.load(f)
        return frequencies

    def cast(self, group):
        cluster_size = len(self.groups_colors[group])
        minor_group_size = len(Vim.groups[group])
        return [self.groups_colors[group][i % cluster_size]
                for i in range(minor_group_size)]
