from hapycolor import config
from hapycolor import helpers

class Vim:
    header = '''
set background=dark
if exists("syntax_on")
syntax reset
endif
let g:colors_name = "hapycolor"'''

    foreground = "Normal"
    groups = [["Comment"],
                   ["Boolean"],
                   ["Character"],
                   ["Keyword"],
                   ["Number"],
                   ["String"],
                   ["Conditional"],
                   ["Macro"],
                   ["Constant", "Define"],
                   ["Cursor"],
                   ["Delimiter", "Directory"],
                   ["Error", "ErrorMsg", "Exception"],
                   ["Float"],
                   ["Function", "MatchParen"],
                   ["Identifier"],
                   ["Label","Operator"]]

    @staticmethod
    def profile(palette, name, img):
        assert(len(palette["colors"]) == len(Vim.groups))
        with open(config.vim(), "w+") as f:
            f.write(Vim.header + "\n\n")
            l = ["hi " + Vim.foreground, "guifg=" + helpers.rgb_to_hex(palette["foreground"]) + "\n"]
            f.write("{: <20}  {: <20}".format(*l))
            for i, G in enumerate(Vim.groups):
                for g in G:
                    l = ["hi " + g, "guifg=" + helpers.rgb_to_hex(palette["colors"][i]) + "\n"]
                    f.write("{: <20}  {: <20}".format(*l))
