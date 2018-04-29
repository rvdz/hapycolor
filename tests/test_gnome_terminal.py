from random import randint
import unittest
from unittest import mock
from hapycolor.targets.gnome_terminal import GnomeTerminal
from hapycolor import palette
from hapycolor import config
from hapycolor import targets

class TestGnome(unittest.TestCase):
    mock_profiles = [{"test1", "test2"}, {"test1", "test2", "test3"}]
    new_profile = None
    def mock_set_profile(profile):
        TestGnome.new_profile = profile
    mock_config = {GnomeTerminal.default_key: "True"}


    terminal_path = "hapycolor.targets.gnome_terminal.GnomeTerminal"

    @mock.patch(terminal_path + ".create_profile")
    @mock.patch(terminal_path + ".get_profiles", side_effect=mock_profiles)
    @mock.patch(terminal_path + ".set_as_default", mock_set_profile)
    @mock.patch(terminal_path + ".load_config", lambda: TestGnome.mock_config)
    def test_set_new_default(self, mock_get, mock_set):
        pltte = palette.Palette()
        GnomeTerminal.export(pltte, "path/to/image")
        self.assertEqual(TestGnome.new_profile, "test3")

    @unittest.skipIf(targets.os() != targets.OS.LINUX, "Needs dconf")
    @mock.patch("hapycolor.config.get_config", config.get_default_config)
    def test_export(self):
        try:
            mock_palette = palette.Palette()
            def color_generator():
                return randint(0, 255), randint(0, 255), randint(0, 255)

            mock_palette.colors = [color_generator() for _ in range(12)]
            mock_palette.foreground = (255, 255, 255)
            mock_palette.background = (0, 0, 0)

            # Saving current profiles
            old_profiles = GnomeTerminal.get_profiles()

            # Creating test profile
            GnomeTerminal.create_profile(mock_palette, "image")

            # Removing created test profile
            new_profile = (GnomeTerminal.get_profiles() - old_profiles).pop()
            GnomeTerminal.remove_profile(new_profile)
        except Exception as exc:
            self.fail(str(exc))

    @unittest.skipIf(targets.os != targets.OS.LINUX, "Needs dconf")
    def test_get_profiles(self):
        profiles = GnomeTerminal.get_profiles()
        self.assertIsInstance(profiles, set)
        self.assertIsInstance(profiles.pop(), str)

    @unittest.skipIf(targets.os != targets.OS.LINUX, "Needs dconf")
    def test_get_new_profile(self):
        profiles = GnomeTerminal.get_profiles()
        new_profiles = set(profiles)
        new_profiles.add("test_profile")
        self.assertEqual((new_profiles - profiles).pop(), "test_profile")

    # def test_echo_export(self):
    #     pltte = palette.Palette()
    #     pltte.colors = [(0, 125-i, i) for i in range(0, 125, 5)]
    #     pltte.foreground = (255, 255, 255)
    #     pltte.background = (0, 0, 0)
    #     GnomeTerminal.export(pltte, "path/to/image.png")
