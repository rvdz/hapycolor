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

    test_file = "./tests/test_replace_line.txt"

    @contextlib.contextmanager
    def test_context(lines=None):
        text = """first line
second line
third line
fourth line
"""
        with open(TestI3.test_file, 'w') as f:
            f.write(text)
            if lines:
                f.write(lines)

        with mock.patch("hapycolor.targets.i3.I3.load_config",
                return_value={I3.configuration_key: TestI3.test_file}):
            yield
        os.remove(TestI3.test_file)

    @test_context()
    def test_replace_line_not_declared(self):
        I3.replace_line("variable (.*)", \
                lambda m: m.group(1) if m else "24")

        subs_done = 0
        with open(TestI3.test_file, 'r') as f:
            for l in f:
                # Exclude '\n'
                if l[:-1] == "24":
                    subs_done += 1
        self.assertEqual(subs_done, 1)

    @test_context("variable 42")
    def test_replace_line_declared_once(self):
        I3.replace_line("variable (.*)",
                            lambda m: m.group(1))

        subs_done = 0
        with open(TestI3.test_file, 'r') as f:
            for l in f:
                if "42" in l:
                    subs_done += 1
        self.assertEqual(subs_done, 1)

    @test_context()
    def test_declare_border_colors_no_rgb(self):
        with self.assertRaises(exceptions.ColorFormatError):
            I3.declare_border_colors("AAbbcc", "0xFFFFFF")

    @test_context()
    def test_declare_border_colors_first(self):
        I3.declare_border_colors((250, 250, 250), (12, 0, 1))
        self._test_declare_border()

    @test_context("set {}    #00FF00".format(I3.split_variable) + "\nLast line")
    def test_declare_border_colors_redeclare_one(self):
        I3.declare_border_colors((250, 250, 250), (12, 0, 1))
        self._test_declare_border()

    @test_context("set {}    #FF00FF\nset {}    #123456\nLastLine"
                  .format(I3.split_variable, I3.border_variable))
    def test_declare_border_colors_redeclare_both(self):
        I3.declare_border_colors((250, 250, 250), (12, 0, 1))
        self._test_declare_border()

    def _test_declare_border(self):
        res1 = "set {}    #fafafa".format(I3.border_variable, (250, 250, 250))
        res2 = "set {}    #0c0001".format(I3.split_variable, (12, 0, 1))

        match1 = 0
        match2 = 0
        with open(TestI3.test_file, 'r') as f:
            for l in f:
                match1 += 1 if res1 in l else 0
                match2 += 1 if res2 in l else 0
        self.assertEqual(match1, 1)
        self.assertEqual(match2, 1)

    @test_context()
    def test_assign_border_colors_first_time(self):
        I3.assign_border_colors()
        expected = "client.focused    {}    {}    #000000    {}" \
                .format(I3.border_variable, I3.border_variable,
                        I3.split_variable)
        self._test_assign_border_colors(expected)

    @test_context("\nclient.focused    #bbbbbb    #cccccc    #ababab    #ffffff")
    def test_assign_border_colors_second_time(self):
        I3.assign_border_colors()
        not_expected = "client.focused    #bbbbbb    #cccccc    #ababab    #ffffff"
        expected = "client.focused    {}    {}    #ababab    {}" \
                .format(I3.border_variable, I3.border_variable,
                        I3.split_variable)
        self._test_assign_border_colors(expected, not_expected)

    @test_context("\nclient.focused    #bbbbbb    #cccccc    #bbbbbb    #ffffff\n"
                  + "Last line")
    def test_assign_border_colors_second_time_not_last_line(self):
        I3.assign_border_colors()
        not_expected = "client.focused    #bbbbbb    #cccccc    #bbbbbb    #ffffff"
        expected = "client.focused    {}    {}    #bbbbbb    {}" \
                .format(I3.border_variable, I3.border_variable,
                        I3.split_variable)
        self._test_assign_border_colors(expected, not_expected)


    def _test_assign_border_colors(self, expected, not_expected=None):
        match = 0
        with open(TestI3.test_file, 'r') as f:
            for l in f.readlines():
                match += 1 if expected in l else 0
                if not_expected is not None and not_expected in l:
                    self.fail("Previous assignement has not been replaced {}"
                              .format(l))
        self.assertEqual(match, 1)

    @test_context("exec --no-startup-id feh --bg-fill --no-xinerama "
        + "~/Pictures/wallpapers/0JSyoDH.jpg\nLast line")
    def test_set_wallpaper(self):
        I3.set_wallpaper("/path/to/image.jpg")
        not_expected = "exec --no-startup-id feh --bg-fill --no-xinerama " \
                + "~/Pictures/wallpapers/0JSyoDH.jpg"
        expected = "exec --no-startup-id feh --bg-fill --no-xinerama " \
                + "/path/to/image.jpg"
        match = 0
        with open(TestI3.test_file, 'r') as f:
            for l in f.readlines():
                match += 1 if expected in l else 0
                if not_expected in l:
                    self.fail("Previous image has not been replaced: {}"
                              .format(l))
        self.assertEqual(match, 1)

    @test_context("status_command yabar")
    @mock.patch("hapycolor.targets.yabar.Yabar.load_config",
        return_value={targets.yabar.Yabar.configuration_key: "test.conf"})
    def test_set_yabar(self, mock_config):
        I3.set_yabar()
        expected = "status_command yabar -c hapy.conf"
        match = 0
        with open(TestI3.test_file, 'r') as f:
            for l in f.readlines():
                match += 1 if expected in l else 0
        self.assertEqual(match, 1)

    def test_is_config_initialized_default(self):
        self.assertFalse(I3.is_config_initialized())

    @test_context()
    def test_export_only_border_empty_config(self):
        mm = Mock()
        mm.colors = [(100, 100, 100), (200, 200, 200)]
        I3.export(mm, "/path/to/image.png")

        with open(TestI3.test_file, 'r') as f:
            expected_1 = "set \$border_color *#646464\n"
            expected_2 = "set \$split_color *#c8c8c8\n"
            expected_3 = "client\.focused.*\$border_color.*\$border_color.*" \
                    "#000000.*\$split_color.*"
            expected = [expected_1, expected_2, expected_3]
            matches = 0
            for l in f.readlines():
                for i, p in enumerate(expected):
                    if re.match(p, l):
                        matches += 1
                        del expected[i]
        self.assertEqual(matches, 3)

    # @mock.patch("hapycolor.targets.yabar.Yabar.is_enabled", returns_value=True)
    # def test_export_yabar(self):
    #     mm = Mock()
    #     mm.colors = MagicMock(return_value=[(100, 100, 100), (200, 200, 200)])
    #     I3.export(mm, "/path/to/image.png")

    @test_context()
    @mock.patch("hapycolor.targets.wallpaper.Wallpaper.is_enabled",
                returns_value=True)
    def test_export_wallpaper(self, mock_enabled):
        mm = Mock()
        mm.colors = [(100, 100, 100), (200, 200, 200)]
        I3.export(mm, "/path/to/image.png")
        with open(TestI3.test_file, 'r') as f:
            expected = "exec --no-startup-id feh --bg-fill --no-xinerama /path/to/image.png\n"
            matches = 0
            for l in f.readlines():
                if expected in l:
                    matches += 1
        self.assertEqual(matches, 1)
