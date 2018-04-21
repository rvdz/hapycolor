import unittest
import re
import pathlib
import os
import contextlib
from unittest import mock
from unittest.mock import Mock
from unittest.mock import MagicMock
import tests.helpers
from hapycolor import config
from hapycolor import helpers
from hapycolor import exceptions
from hapycolor import targets
from hapycolor.targets.i3 import I3

class TestI3(unittest.TestCase):

    @contextlib.contextmanager
    def i3context(in_list, out_list):
        mock_file = mock.Mock()
        mock_file.write = lambda string: out_list.append(string)

        @contextlib.contextmanager
        def mock_open(file, mode):
            yield mock_file

        @contextlib.contextmanager
        def mock_edit_config(file):
            yield (in_list, out_list)

        load_config = "hapycolor.targets.i3.I3.load_config"
        i3_config = {I3.configuration_key: "tests/test_i3.txt"}
        edit_config = "hapycolor.config.ConfigurationEditor.edit_config"
        wallpaper_enabled = "hapycolor.targets.wallpaper.Wallpaper.is_enabled"
        yabar_enabled = "hapycolor.targets.yabar.Yabar.is_enabled"
        with mock.patch(load_config, return_value=i3_config),\
                mock.patch(edit_config, mock_edit_config), \
                mock.patch("builtins.open", mock_open), \
                mock.patch(wallpaper_enabled, return_value=True), \
                mock.patch(yabar_enabled, return_value=False):
            yield

    def test_declare_color_colors_no_rgb(self):
        result = []
        with self.assertRaises(exceptions.ColorFormatError), \
            TestI3.i3context([], result):
            I3.declare_color(I3.border_variable, "#AAbbcc")
            I3.declare_color(I3.split_variable, "0xFFFFFF")

    def test_declare_color_colors_first(self):
        text = ["first line", "second line", "third line", "fourth line"]
        result = []
        with TestI3.i3context(text, result):
            I3.declare_color(I3.border_variable, (250, 250, 250))
            I3.declare_color(I3.split_variable, (12, 0, 1))

        res1 = "set {}    #fafafa".format(I3.border_variable)
        res2 = "set {}    #0c0001".format(I3.split_variable)
        self.assertEqual(result[9], res2)
        self.assertEqual(result[4], res1)

    def test_declare_color_colors_redeclare_one(self):
        text = ["first line", "second line", "third line", "fourth line",
                "set {}    #00FF00".format(I3.split_variable), "Last line"]
        result = []
        with TestI3.i3context(text, result):
            I3.declare_color(I3.border_variable, (250, 250, 250))
            I3.declare_color(I3.split_variable, (12, 0, 1))

        res1 = "set {}    #fafafa".format(I3.border_variable)
        res2 = "set {}    #0c0001".format(I3.split_variable)
        self.assertEqual(result[11], res2)
        self.assertEqual(result[6], res1)

    def test_declare_color_colors_redeclare_both(self):
        text = ["first line", "second line", "third line", "fourth line",
                "set {}    #FF00FF".format(I3.split_variable),
                "set {}    #123456".format(I3.border_variable), "LastLine"]

        result = []
        with TestI3.i3context(text, result):
            I3.declare_color(I3.border_variable, (250, 250, 250))
            I3.declare_color(I3.split_variable, (12, 0, 1))

        res1 = "set {}    #fafafa".format(I3.border_variable)
        res2 = "set {}    #0c0001".format(I3.split_variable)
        self.assertEqual(result[11], res2)
        self.assertEqual(result[5], res1)

    def test_assign_border_colors_first_time(self):
        text = ["first line", "second line", "third line", "fourth line"]
        result = []
        with TestI3.i3context(text, result):
            I3.assign_border_colors()

        expected = "client.focused    {}    {}    #000000    {}" \
                .format(I3.border_variable, I3.border_variable,
                        I3.split_variable)
        self.assertEqual(result[4], expected)

    def test_assign_border_colors_second_time(self):
        text = ["first line", "second line", "third line", "fourth line",
                "client.focused    #bbbbbb    #cccccc    #ababab    #ffffff"]
        result = []
        with TestI3.i3context(text, result):
            I3.assign_border_colors()

        not_expected = "client.focused    #bbbbbb    #cccccc    #ababab    #ffffff"
        expected = "client.focused    {}    {}    #ababab    {}" \
                .format(I3.border_variable, I3.border_variable,
                        I3.split_variable)
        self.assertNotEqual(result[4], not_expected)
        self.assertEqual(result[4], expected)

    def test_assign_border_colors_second_time_not_last_line(self):
        text = ["first line", "second line", "third line", "fourth line",
                "client.focused    #bbbbbb    #cccccc    #bbbbbb    #ffffff",
                "Last line"]
        result = []

        with TestI3.i3context(text, result):
            I3.assign_border_colors()

        not_expected = "client.focused    #bbbbbb    #cccccc    #bbbbbb    #ffffff"
        expected = "client.focused    {}    {}    #bbbbbb    {}" \
                .format(I3.border_variable, I3.border_variable,
                        I3.split_variable)
        self.assertNotEqual(result[4], not_expected)
        self.assertEqual(result[4], expected)

    def test_set_wallpaper(self):
        text = ["first line", "second line", "third line", "fourth line",
                "exec --no-startup-id feh --bg-fill --no-xinerama \
                ~/Pictures/wallpapers/0JSyoDH.jpg", "Last line"]
        result = []
        with TestI3.i3context(text, result):
            I3.set_wallpaper("/path/to/image.jpg")

        not_expected = "exec --no-startup-id feh --bg-fill --no-xinerama " \
                + "~/Pictures/wallpapers/0JSyoDH.jpg"
        expected = "exec --no-startup-id feh --bg-fill --no-xinerama " \
                + "/path/to/image.jpg"
        self.assertNotEqual(result[4], not_expected)
        self.assertEqual(result[4], expected)

    @mock.patch("hapycolor.targets.yabar.Yabar.load_config",
        return_value={targets.yabar.Yabar.configuration_key: "test.conf"})
    def test_set_yabar(self, mock_config):
        text = ["first line", "second line", "third line", "fourth line",
                "status_command yabar"]
        result = []
        with TestI3.i3context(text, result):
            I3.set_yabar()

        expected = "status_command yabar -c hapy.conf"
        self.assertEqual(result[4], expected)

    def test_is_config_initialized_default(self):
        self.assertFalse(I3.is_config_initialized())

    def test_export_only_border_empty_config(self):
        mm = Mock()
        mm.colors = [(100, 100, 100), (200, 200, 200)]
        result = []
        with TestI3.i3context([], result):
            I3.export(mm, "/path/to/image.png")

        expected = [ "client.focused    $border_color    $border_color    "
                        + "#000000    $split_color",
                    "set $border_color    #646464",
                    "set $split_color    #c8c8c8",
                    "exec --no-startup-id feh --bg-fill --no-xinerama "
                        + "/path/to/image.png"]
        self.assertEqual(result, expected)

    @mock.patch("hapycolor.targets.wallpaper.Wallpaper.is_enabled",
                returns_value=True)
    def test_export_wallpaper(self, mock_enabled):
        mm = Mock()
        mm.colors = [(100, 100, 100), (200, 200, 200)]

        result = []
        with TestI3.i3context([], result):
            I3.set_wallpaper("/path/to/image.png")

        expected = "exec --no-startup-id feh --bg-fill --no-xinerama /path/to/image.png"
        self.assertEqual(result[0], expected)
