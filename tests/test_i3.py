import unittest
import pathlib
import os
import contextlib
from unittest import mock
from hapycolor import helpers
from hapycolor import exceptions
from hapycolor import targets
from hapycolor.targets.i3 import I3

class TestI3(unittest.TestCase):

    test_config = "./tests/i3_config.txt"
    test_file = "./tests/test_replace_line.txt"

    @contextlib.contextmanager
    def test_context(lines=None):
        text = """
first line
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
    def test_declare_border_colors_no_hex(self):
        with self.assertRaises(exceptions.ColorFormatError):
            I3.declare_border_colors("AAbbcc", "0xFFFFFF")

    @test_context()
    def test_declare_border_colors_first(self):
        I3.declare_border_colors("0x000000", "0xFFFFFF")
        self._test_declare_border()

    @test_context(I3.split_variable)
    def test_declare_border_colors_redeclare_one(self):
        I3.declare_border_colors("0x000000", "0xFFFFFF")
        self._test_declare_border()

    @test_context("{}\n{}".format(I3.split_variable, I3.border_variable))
    def test_declare_border_colors_redeclare_both(self):
        I3.declare_border_colors("0x000000", "0xFFFFFF")
        self._test_declare_border()

    def _test_declare_border(self):
        res1 = "set {} = {}".format(I3.border_variable, "0x000000")
        res2 = "set {} = {}".format(I3.split_variable, "0xFFFFFF")

        match1 = False
        match2 = False
        with open(TestI3.test_file, 'r') as f:
            for l in f:
                match1 |= res1 in l
                match2 |= res2 in l
        self.assertTrue(match1)
        self.assertTrue(match2)

    @test_context()
    def test_assign_border_colors_first_time(self):
        I3.assign_border_colors()
        expected = "client.focused\t{}\t{}\t0x000000\t{}" \
                .format(I3.border_variable, I3.border_variable,
                        I3.split_variable)
        self._test_assign_border_colors(expected)

    @test_context("client.focused\t0xbbbbbb\t0xcccccc\t0xababab\t0xffffff")
    def test_assign_border_colors_second_time(self):
        I3.assign_border_colors()
        expected = "client.focused\t{}\t{}\t0xababab\t{}" \
                .format(I3.border_variable, I3.border_variable,
                        I3.split_variable)
        self._test_assign_border_colors(expected)

    def _test_assign_border_colors(self, expected):
        match = False
        with open(TestI3.test_file, 'r') as f:
            for l in f.readlines():
                match |= expected in l
        self.assertTrue(match)

    @test_context("exec --no-startup-id feh --bg-fill --no-xinerama "
        + "~/Pictures/wallpapers/0JSyoDH.jpg")
    def test_set_wallpaper(self):
        I3.set_wallpaper("/path/to/image.jpg")
        expected = "exec --no-startup-id feh --bg-fill --no-xinerama " \
                + "/path/to/image.jpg"
        match = False
        with open(TestI3.test_file, 'r') as f:
            for l in f.readlines():
                match |= expected in l
        self.assertTrue(match)

    @test_context("exec yabar")
    @mock.patch("hapycolor.targets.yabar.Yabar.load_config",
        return_value={targets.yabar.Yabar.configuration_key: "test.conf"})
    def test_set_yabar(self, mock_config):
        I3.set_yabar()
        expected = "yabar -c test.conf"
        match = False
        with open(TestI3.test_file, 'r') as f:
            for l in f.readlines():
                match |= expected in l
        self.assertTrue(match)
