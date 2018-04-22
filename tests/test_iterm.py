import unittest
from unittest import mock
import pathlib
import contextlib
import os
import shutil
from hapycolor import exceptions, config, helpers, palette
from hapycolor import targets
from hapycolor.targets.iterm import Iterm
from hapycolor.targets.terminal import Terminal
from tests.helpers import generate_palette, configurationtesting, disableprints


@contextlib.contextmanager
def itermtesting(fails=0, default=True):
    valid_entry = ["./tests/com.googlecode.iterm2.plist"]
    invalid_entry = ["."]
    entries = invalid_entry * fails + valid_entry

    test_config_path = (config.ROOT_DIR
                        / "../tests/com.googlecode.iterm2.plist").as_posix()
    tmp_test_config_path = (config.ROOT_DIR
                            / "../tests/com.googlecode.iterm2.tmp").as_posix()
    shutil.copyfile(test_config_path, tmp_test_config_path)

    with mock.patch('builtins.input', side_effect=entries):
        with mock.patch('hapycolor.targets.iterm.Iterm.set_default',
                        return_value=default):
            yield
    shutil.copyfile(tmp_test_config_path, test_config_path)
    os.remove(tmp_test_config_path)


class TestIterm(unittest.TestCase):
    @itermtesting()
    @configurationtesting()
    def test_valid_template(self):
        """ Checks that the template file is valid """
        import xml.etree.ElementTree as ET
        try:
            ET.parse(Iterm.load_config()[Iterm.template_key])
        except ET.ParseError as err:
            self.fail(str(err))

    plutil_reason = "To decode the file preferences, Darwin's command " \
            + "'plutil' is needed"

    @itermtesting()
    @configurationtesting()
    def test_valid_basic_configuration(self):
        """ Checks that the basic configuration file is valid """
        import xml.etree.ElementTree as ET
        try:
            Iterm.initialize_config()
            ET.parse(Iterm.load_config()[Iterm.preferences_key])
        except ET.ParseError as err:
            self.fail(str(err))

    @unittest.skipUnless(targets.os() == targets.OS.DARWIN, plutil_reason)
    @itermtesting()
    @configurationtesting()
    def test_export_iterm_0_color_palette(self):
        with self.assertRaises(exceptions.ColorFormatError):
                Iterm.export(generate_palette(0), "iterm_test")

    @unittest.skipUnless(targets.os() == targets.OS.DARWIN, plutil_reason)
    @itermtesting()
    @configurationtesting()
    def test_export_iterm_1_color_palette(self):
        with self.assertRaises(exceptions.InvalidPaletteException):
                Iterm.initialize_config()
                Iterm.export(generate_palette(1), "iterm_test")

    @unittest.skipUnless(targets.os() == targets.OS.DARWIN, plutil_reason)
    @itermtesting()
    @configurationtesting()
    def test_export_iterm_12_color_palette(self):
        colors = [(0, 0.5, 0.5), (10, 0.5, 0.7),
                  (60, 0.5, 0.5), (70, 0.5, 0.7),
                  (100, 0.5, 0.5), (110, 0.5, 0.7),
                  (170, 0.5, 0.5), (180, 0.5, 0.7),
                  (250, 0.5, 0.5), (260, 0.5, 0.7),
                  (300, 0.5, 0.5), (310, 0.5, 0.7)]
        colors = [helpers.hsl_to_rgb(c) for c in colors]
        pltte = mock.Mock()
        pltte.colors = colors
        pltte.background = (0, 0, 0)
        pltte.foreground = (255, 255, 255)
        pltte.__class__ = palette.Palette
        pltte.is_initialized = mock.MagicMock(return_value=True)
        try:
            Iterm.initialize_config()
            Iterm.export(pltte, "iterm_test")
        except Exception as err:
            self.fail(str(err))

    @unittest.skipUnless(targets.os() == targets.OS.DARWIN, plutil_reason)
    @itermtesting()
    @configurationtesting()
    def test_export_iterm_16_color_palette(self):
        colors = [(0, 0.5, 0.5), (10, 0.5, 0.7),
                  (60, 0.5, 0.5), (70, 0.5, 0.7),
                  (30, 0.5, 0.5), (40, 0.5, 0.7),
                  (100, 0.5, 0.5), (110, 0.5, 0.7),
                  (170, 0.5, 0.5), (180, 0.5, 0.7),
                  (210, 0.5, 0.5), (220, 0.5, 0.7),
                  (250, 0.5, 0.5), (260, 0.5, 0.7),
                  (300, 0.5, 0.5), (310, 0.5, 0.7)]
        colors = [helpers.hsl_to_rgb(c) for c in colors]
        pltte = mock.Mock()
        pltte.colors = colors
        pltte.background = (0, 0, 0)
        pltte.foreground = (255, 255, 255)
        pltte.__class__ = palette.Palette
        pltte.is_initialized = mock.MagicMock(return_value=True)
        try:
            Iterm.initialize_config()
            Iterm.export(pltte, "iterm_test")
        except Exception as err:
            self.fail(str(err))

    @itermtesting(default=True)
    @configurationtesting()
    def test_is_default_is_boolean_true(self):
        Iterm.initialize_config()
        self.assertEqual(Iterm.load_config()[Iterm.default_key], str(True))

    @itermtesting(default=False)
    @configurationtesting()
    def test_is_default_is_boolean_false(self):
        Iterm.initialize_config()
        self.assertEqual(Iterm.load_config()[Iterm.default_key], str(False))

    @disableprints()
    @configurationtesting()
    def test_default_profile_toggle(self):
        with itermtesting(default=True):
            Iterm.initialize_config()
        self.assertEqual(Iterm.load_config()[Iterm.default_key], str(True))
        with mock.patch('builtins.input', return_value="2"):
            Iterm.reconfigure()
        self.assertEqual(Iterm.load_config()[Iterm.default_key], str(False))


class TestTermColor(unittest.TestCase):
    def test_color_format(self):
        with self.assertRaises(exceptions.ColorFormatError):
            Terminal([(240, 240, 0.3), (0, 0, 1)])

    def test_invalid_argument(self):
        with self.assertRaises(exceptions.WrongInputError):
            Terminal((12, 14, 16))

    def test_not_enough_arguments(self):
        colors = [(100, 100, 100), (200, 200, 200), (150, 100, 50)]
        with self.assertRaises(exceptions.InvalidPaletteException):
            Terminal(colors)

    def test_classify_hue(self):
        colors = [(0, 0.5, 0.5), (10, 0.5, 0.5),
                  (60, 0.5, 0.5), (70, 0.5, 0.5),
                  (100, 0.5, 0.5), (110, 0.5, 0.5),
                  (170, 0.5, 0.5), (180, 0.5, 0.5),
                  (250, 0.5, 0.5), (260, 0.5, 0.5),
                  (300, 0.5, 0.5), (310, 0.5, 0.5)]
        colors = [helpers.hsl_to_rgb(c) for c in colors]
        classified = Terminal._classify_hue(colors)
        self.assertEqual(len(classified), 6)

    def test_classify_hue_1_color_cluster(self):
        colors = [(0, 0.5, 0.5), (60, 0.5, 0.5),
                  (100, 0.5, 0.5), (170, 0.5, 0.5),
                  (250, 0.5, 0.5), (300, 0.5, 0.5)]
        colors = [helpers.hsl_to_rgb(c) for c in colors]
        classified = Terminal._classify_hue(colors)
        self.assertEqual(len(classified), 6)

    def test_classify_luminosity(self):
        colors = [(0, 0.5, 0.5), (10, 0.5, 0.7),
                  (60, 0.5, 0.5), (70, 0.5, 0.7),
                  (100, 0.5, 0.5), (110, 0.5, 0.7),
                  (170, 0.5, 0.5), (180, 0.5, 0.7),
                  (250, 0.5, 0.5), (260, 0.5, 0.7),
                  (300, 0.5, 0.5), (310, 0.5, 0.7)]
        colors = [helpers.hsl_to_rgb(c) for c in colors]
        classified_hue = Terminal._classify_hue(colors)
        classified_lum = Terminal._classify_luminosity(classified_hue)
        self.assertEqual(len(classified_lum), 6)
        for (c1, c2) in classified_lum:
            self.assertNotEqual(c1, c2)
            self.assertLess(c1[2], c2[2])

    def test_classify_luminosity_1_color_cluster(self):
        colors = [(0, 0.5, 0.5), (60, 0.5, 0.5),
                  (100, 0.5, 0.5), (170, 0.5, 0.5),
                  (250, 0.5, 0.5), (300, 0.5, 0.5)]
        colors = [helpers.hsl_to_rgb(c) for c in colors]
        classified_hue = Terminal._classify_hue(colors)
        classified_lum = Terminal._classify_luminosity(classified_hue)
        self.assertEqual(len(colors), 6)
        for (c1, c2) in classified_lum:
            self.assertEqual(c1, c2)

    def test_sort_medoids(self):
        colors = [(0, 0.5, 0.5), (10, 0.5, 0.7),
                  (60, 0.5, 0.5), (70, 0.5, 0.7),
                  (100, 0.5, 0.5), (110, 0.5, 0.7),
                  (170, 0.5, 0.5), (180, 0.5, 0.7),
                  (250, 0.5, 0.5), (260, 0.5, 0.7),
                  (300, 0.5, 0.5), (310, 0.5, 0.7)]
        colors = [helpers.hsl_to_rgb(c) for c in colors]
        classified_hue = Terminal._classify_hue(colors)
        classified_lum = Terminal._classify_luminosity(classified_hue)
        sorted_colors = Terminal._sort_medoids(classified_lum)
        self.assertEqual(len(sorted_colors), 16)

        hsl_sorted = [helpers.rgb_to_hsl(c) for c in sorted_colors]
        for i in range(8):
            self.assertLessEqual(hsl_sorted[i][2], hsl_sorted[i+8][2])

    def test_sort_no_geen_components(self):
        colors = [(0, 0.5, 0.5), (10, 0.5, 0.7),
                  (40, 0.5, 0.5), (50, 0.5, 0.7),
                  (170, 0.5, 0.5), (180, 0.5, 0.7),
                  (250, 0.5, 0.5), (260, 0.5, 0.7),
                  (300, 0.5, 0.5), (310, 0.5, 0.7),
                  (340, 0.5, 0.5), (350, 0.5, 0.7)]
        colors = [helpers.hsl_to_rgb(c) for c in colors]
        classified_hue = Terminal._classify_hue(colors)
        classified_lum = Terminal._classify_luminosity(classified_hue)
        sorted_colors = Terminal._sort_medoids(classified_lum)
        self.assertEqual(len(sorted_colors), 16)

        hsl_sorted = [helpers.rgb_to_hsl(c) for c in sorted_colors]
        # Testing red component
        self.assertTrue(hsl_sorted[1][0] < 25 or hsl_sorted[1][0] > 345)
        self.assertTrue(hsl_sorted[9][0] < 25 or hsl_sorted[9][0] > 345)
        # Testing green component
        self.assertEqual(hsl_sorted[2], (140, 1, 0.3))
        self.assertEqual(hsl_sorted[10], (120, 1, 0.7))

    def test_sort_special_components(self):
        colors = [(0, 0.5, 0.5), (10, 0.5, 0.7),
                  (60, 0.5, 0.5), (70, 0.5, 0.7),
                  (100, 0.5, 0.5), (110, 0.5, 0.7),
                  (170, 0.5, 0.5), (180, 0.5, 0.7),
                  (250, 0.5, 0.5), (260, 0.5, 0.7),
                  (300, 0.5, 0.5), (310, 0.5, 0.7)]
        colors = [helpers.hsl_to_rgb(c) for c in colors]
        classified_hue = Terminal._classify_hue(colors)
        classified_lum = Terminal._classify_luminosity(classified_hue)
        sorted_colors = Terminal._sort_medoids(classified_lum)
        self.assertEqual(len(sorted_colors), 16)

        hsl_sorted = [helpers.rgb_to_hsl(c) for c in sorted_colors]
        # Testing red component
        self.assertTrue(hsl_sorted[1][0] < 25 or hsl_sorted[1][0] > 345)
        self.assertTrue(hsl_sorted[9][0] < 25 or hsl_sorted[9][0] > 345)
        # Testing green component
        self.assertTrue(hsl_sorted[2][0] < 160 and hsl_sorted[2][0] > 60)
        self.assertTrue(hsl_sorted[10][0] < 160 and hsl_sorted[10][0] > 60)

    def test_init_6_colors(self):
        colors = [(0, 0.5, 0.5), (60, 0.5, 0.5),
                  (100, 0.5, 0.5), (170, 0.5, 0.5),
                  (250, 0.5, 0.5), (300, 0.5, 0.5)]
        colors = [helpers.hsl_to_rgb(c) for c in colors]
        cm = Terminal(colors)
        self.assertEqual(len(cm.colors), 16)
        self.assertEqual(len(set(cm.colors)), 10)

    def test_init_12_colors(self):
        colors = [(0, 0.5, 0.5), (10, 0.5, 0.7),
                  (60, 0.5, 0.5), (70, 0.5, 0.7),
                  (100, 0.5, 0.5), (110, 0.5, 0.7),
                  (170, 0.5, 0.5), (180, 0.5, 0.7),
                  (250, 0.5, 0.5), (260, 0.5, 0.7),
                  (300, 0.5, 0.5), (310, 0.5, 0.7)]
        colors = [helpers.hsl_to_rgb(c) for c in colors]
        cm = Terminal(colors)
        self.assertEqual(len(cm.colors), 16)
        self.assertEqual(len(set(cm.colors)), 16)
        for c in cm.colors:
            self.assertTrue(helpers.can_be_rgb(c))

    @configurationtesting()
    @unittest.skipUnless(targets.os() == targets.OS.DARWIN, "Tests Darwin's"
                         + " environment")
    def test_configuration_iterm_template(self):
        raw_path = Iterm.load_config()[Iterm.template_key]
        iterm_template_path = pathlib.Path(raw_path).resolve()
        self.assertTrue(iterm_template_path.exists())
