import unittest
from hapycolor.configuration_editor import ConfigurationEditor
from hapycolor import exceptions
from hapycolor import palette

class TestConfigurationEditor(unittest.TestCase):
    def test_is_macro_correct(self):
        entries = ["# @hapycolor(\"random\")", "!      @hapycolor()",
                   "@ @hapycolor(None)   "]
        for entry in entries:
            self.assertTrue(ConfigurationEditor.is_macro(entry))

    def test_from_macro(self):
        entries = ["# @hapycolor(\"random\")",
                   "!      @hapycolor(\"random\")",
                   "!      @hapycolor(\"background\")",
                   "@ @hapycolor(\"foreground\", None, \"random\")"]

        expected = [["random"], ["random"],
                    ["background"], ["foreground", None, "random"]]

        for entry, exp in zip(entries, expected):
            self.assertEqual(ConfigurationEditor.from_macro(entry), exp)

    def test_get_format_rgb(self):
        # (r, g, b)
        lines = ["(12, 34, 56)", "         (43, 12,200)   ",
                 " (  12  ,  255  ,    0)"]
        for line in lines:
            try:
                _, converter = ConfigurationEditor.get_format(line)
                result = converter((12, 34, 45))
            except exceptions.ColorFormatNotFound:
                self.fail("converter not found")
            expected = "(12, 34, 45)"
            self.assertEqual(result, expected)

    def test_get_format_rgb_alpha(self):
        # (r, g, b, alpha)
        lines = ["(12, 34, 56, 0%)", "   (43, 12, 200,100%)   ",
                 " (  12  ,  255  , 0, 50% )"]
        for line in lines:
            try:
                _, converter = ConfigurationEditor.get_format(line)
                result = converter((12, 34, 45))
            except exceptions.ColorFormatNotFound:
                self.fail("converter not found")
            expected = "(12, 34, 45,"
            self.assertEqual(result, expected)

    def test_get_format_hex(self):
        # #RRGGBB
        lines = ["#123456", "  #AAbbCC", "  #ab23cf   "]
        for line in lines:
            try:
                _, converter = ConfigurationEditor.get_format(line)
                result = converter((1, 2, 3))
            except exceptions.ColorFormatNotFound:
                self.fail("converter not found")
            expected = "#010203"
            self.assertEqual(result, expected)

    def test_replace_color(self):
        pass

    def test_replace(self):
        configuration = ["line 1",
                         "# @hapycolor(\"random\")", "#034503",
                         "line 4",
                         "line 5 #aabbcc",
                         "# @hapycolor(\"random\")", "asdf #bcbcbc sfdg",
                         "# @hapycolor(\"foreground\")", "new line #abacbd",
                         "# @hapycolor(\"random\", None, \"background\")",
                         "#123456, #FFAACC, #987654",
                         "# @hapycolor(\"random\")", "Last line: #982345"]
        conf_editor = ConfigurationEditor(configuration)
        pltte = palette.Palette()
        pltte.colors = [(1, 2, 3), (4, 5, 6), (7, 8, 9)]
        pltte.foreground = (255, 255, 255)
        pltte.background = (0, 0, 0)

        new_config = conf_editor.replace(pltte)

        expected = ["line 1",
                    "# @hapycolor(\"random\")", "#010203",
                    "line 4",
                    "line 5 #aabbcc",
                    "# @hapycolor(\"random\")", "asdf #040506 sfdg",
                    "# @hapycolor(\"foreground\")", "new line #ffffff",
                    "# @hapycolor(\"random\", None, \"background\")",
                    "#070809, #FFAACC, #000000",
                    "# @hapycolor(\"random\")", "Last line: #010203"]
        self.assertEqual(new_config, expected)
