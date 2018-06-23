"""
i3 Test Module
"""
import os
import unittest
from unittest import mock
import contextlib
from hapycolor import exceptions
from hapycolor import targets
from hapycolor import palette
from hapycolor.configuration_editor import ConfigFileEditor
from hapycolor.targets.i3 import I3

class TestI3(unittest.TestCase):
    def test_export_wallpaper_set(self):
        config = ["line 1", "exec --no-startup-id feh --bg-fill \
                  /path/to/otherimage.png",
                  "line 3"]
        result = I3.set_wallpaper(config, "/path/to/image.png")

        expected = "exec --no-startup-id feh --bg-fill /path/to/image.png"
        self.assertEqual(result[1], expected)

    def test_replace_color(self):
        config = ["line 1", "# @hapycolor('random')", "set $var_color    #aaaaaa", "Last line"]


        mock_palette = palette.Palette()
        mock_palette.colors = [(4, 6, 7), (1, 3, 6), (3, 6, 8)]

        result = ConfigFileEditor(config).replace(mock_palette)

        expected = ["line 1", "# @hapycolor('random')", "set $var_color    #040607", "Last line"]
        self.assertEqual(result, expected)

    def test_export_with_file_and_no_macro(self):
        config_path = "./tests/test_i3.txt"
        config = ["line 1", "line 3", "set $var_color    #aaaaaa", "Last line"]

        with open(config_path, 'w') as config_file:
            config_file.write('\n'.join(config))

        mock_palette = palette.Palette()
        mock_palette.colors = [(4, 6, 7), (1, 3, 6), (3, 6, 8)]
        mock_config = {I3.configuration_key: config_path}
        with mock.patch("hapycolor.targets.i3.I3.load_config",
                        return_value=mock_config), \
                mock.patch("hapycolor.targets.wallpaper.Wallpaper.is_enabled",
                           return_value=False):
            I3.export(mock_palette, "path/to/image.png")

        with open(config_path, 'r') as config_file:
            result = config_file.read().splitlines()

        expected = ["line 1", "line 3", "set $var_color    #aaaaaa", "Last line"]
        self.assertEqual(result, expected)
        os.remove(config_path)
