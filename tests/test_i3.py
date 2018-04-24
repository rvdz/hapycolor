"""
i3 Test Module
"""
import os
import unittest
from unittest import mock
import contextlib
from hapycolor import exceptions
from hapycolor import targets
from hapycolor.targets import yabar
from hapycolor.targets.i3 import I3

class TestI3(unittest.TestCase):
    def test_declare_color_colors_no_rgb(self):
        with self.assertRaises(exceptions.ColorFormatError):
            I3.declare_color([], I3.border_variable, "#AAbbcc")
            I3.declare_color([], I3.split_variable, "0xFFFFFF")

    def test_declare_color_not_set(self):
        config = ["first line", "second line", "third line", "fourth line"]
        result = I3.declare_color(config, I3.border_variable, (250, 250, 250))

        expected = "set {}    #fafafa".format(I3.border_variable)
        self.assertEqual(result[0], expected)

    def test_declare_color_set(self):
        config = ["first line", "second line", "third line", "fourth line",
                  "set {}    #00FFFF".format(I3.border_variable),
                  "set {}    #00FF00".format(I3.split_variable), "Last line"]
        result = I3.declare_color(config, I3.split_variable, (12, 0, 1))

        expected = "set {}    #0c0001".format(I3.split_variable)
        self.assertEqual(result[5], expected)

    def test_assign_border_colors_not_set(self):
        config = ["first line", "second line", "third line", "fourth line"]

        result = I3.assign_border_colors(config)
        expected = "client.focused    {}    {}    #000000    {}" \
                .format(I3.border_variable, I3.border_variable,
                        I3.split_variable)
        self.assertEqual(result[0], expected)

    def test_assign_border_color_set(self):
        config = ["first line", "second line", "third line", "fourth line",
                  "client.focused    #bbbbbb    #cccccc    #aaaaaa    #ffffff",
                  "Last line"]
        result = I3.assign_border_colors(config)

        expected = "client.focused    {}    {}    #aaaaaa    {}" \
                .format(I3.border_variable, I3.border_variable,
                        I3.split_variable)
        self.assertEqual(result[4], expected)

    @mock.patch("hapycolor.targets.yabar.Yabar.load_config",
                return_value={yabar.Yabar.configuration_key: "/path/to/yabar.conf"})
    def test_set_yabar_not_set(self, mock_config):
        config = ["first line", "second line", "third line", "fourth line"]
        result = I3.set_yabar(config)

        expected = "status_command yabar -c /path/to/hapy.conf"
        self.assertEqual(result[0], expected)

    @mock.patch("hapycolor.targets.yabar.Yabar.load_config",
                return_value={yabar.Yabar.configuration_key: "/path/to/yabar.conf"})
    def test_set_yabar_set(self, mock_config):
        config = ["first line", "second line", "third line", "fourth line",
                  "status_command yabar"]
        result = I3.set_yabar(config)

        expected = "status_command yabar -c /path/to/hapy.conf"
        self.assertEqual(result[4], expected)

    def test_is_config_initialized_default(self):
        self.assertFalse(I3.is_config_initialized())

    def test_declare_variable_not_set(self):
        border_color = (100, 100, 100)
        config = ["line 1", "line 2"]
        result = I3.declare_color(config, I3.border_variable, border_color)
        expected = "set $border_color    #646464"
        self.assertEqual(result[0], expected)

    def test_declare_variable_set(self):
        border_color = (100, 100, 100)
        config = ["line 1", "set $border_color #123455", "line 3"]
        result = I3.declare_color(config, I3.border_variable, border_color)
        expected = "set $border_color    #646464"
        self.assertEqual(result[1], expected)
    def test_export_wallpaper_not_set(self):
        result = []
        config = ["line 1", "line 2"]
        result = I3.set_wallpaper(config, "/path/to/image.png")

        expected = "exec --no-startup-id feh --bg-fill --no-xinerama /path/to/image.png"
        self.assertEqual(result[0], expected)

    def test_export_wallpaper_set(self):
        result = []
        config = ["line 1", "exec --no-startup-id feh --bg-fill --no-xinerama \
                  /path/to/otherimage.png",
                  "line 3"]
        result = I3.set_wallpaper(config, "/path/to/image.png")

        expected = "exec --no-startup-id feh --bg-fill --no-xinerama /path/to/image.png"
        self.assertEqual(result[1], expected)

    def test_export_set(self):
        config = ["line 1", "client.focused    #123456 #999999   "
                  + "#aaaaaa    $split_color",
                  "line 3",
                  "set $border_color    #bbbbbb",
                  "set $var_color    #aaaaaa",
                  "status_command yabar -c /path/to/nothapy.conf",
                  "set $split_color    #cccccc",
                  "exec --no-startup-id feh --bg-fill --no-xinerama "
                  + "/path/to/otherimage.png", "last line"]

        expected = ["line 1", "client.focused    $border_color   "
                    + " $border_color    #aaaaaa    $split_color",
                    "line 3",
                    "set $border_color    #646464",
                    "set $var_color    #aaaaaa",
                    "status_command yabar -c /path/to/hapy.conf",
                    "set $split_color    #c8c8c8",
                    "exec --no-startup-id feh --bg-fill --no-xinerama "
                    + "/path/to/image.png", "last line"]

        result = []
        mock_file = mock.Mock()
        mock_file.write = lambda string: result.extend(string.split('\n'))
        mock_file.read().splitlines = lambda: config

        @contextlib.contextmanager
        def mock_open(file, mode):
            yield mock_file

        palette = mock.Mock()
        palette.colors = [(100, 100, 100), (200, 200, 200)]

        mock_yabar = {yabar.Yabar.configuration_key: "/path/to/yabar.conf"}
        with mock.patch("builtins.open", mock_open), \
                mock.patch("hapycolor.targets.i3.I3.load_config"), \
                mock.patch("hapycolor.targets.wallpaper.Wallpaper.is_enabled", \
                        return_value=True), \
                mock.patch("hapycolor.targets.yabar.Yabar.is_enabled", \
                        return_value=True), \
                mock.patch("hapycolor.targets.yabar.Yabar.load_config",
                           return_value=mock_yabar):
            I3.export(palette, "/path/to/image.png")

        self.assertEqual(result, expected)

    def test_export_with_file(self):
        config_path = "./tests/test_i3.txt"
        config = ["line 1", "line 3", "set $border_color    #bbbbbb",
                  "set $var_color    #aaaaaa", "Last line"]

        with open(config_path, 'w') as config_file:
            config_file.write('\n'.join(config))

        mock_palette = mock.Mock()
        mock_palette.colors = [(4, 6, 7), (1, 3, 6), (3, 6, 8)]
        mock_config = {I3.configuration_key: config_path}
        with mock.patch("hapycolor.targets.i3.I3.load_config",
                        return_value=mock_config), \
                mock.patch("hapycolor.targets.yabar.Yabar.is_enabled",
                           return_value=False), \
                mock.patch("hapycolor.targets.wallpaper.Wallpaper.is_enabled",
                           return_value=False):
            I3.export(mock_palette, "path/to/image.png")

        with open(config_path, 'r') as config_file:
            result = config_file.read().splitlines()

        expected = ["set $split_color    #010306",
                    "client.focused    $border_color   "
                    + " $border_color    #000000    $split_color",
                    "line 1", "line 3", "set $border_color    #040607",
                    "set $var_color    #aaaaaa", "Last line"]
        self.assertEqual(result, expected)
        os.remove(config_path)
