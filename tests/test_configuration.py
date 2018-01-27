from hapycolor import config
from hapycolor import exceptions
from hapycolor.targets.iterm import Iterm
from hapycolor.targets.vim import Vim
from hapycolor.targets.wallpaper import Wallpaper
from tests import helpers
from unittest.mock import patch
import pathlib
import unittest


class TestConfiguration(unittest.TestCase):
    @helpers.configurationtesting()
    def test_hypeplans_files_exist(self):
        """ Checks if manual hyperplan point's file exists """
        for filter_type in config.Filter:
            hyperplan_file = pathlib.Path(config.hyperplan_file(filter_type))
            self.assertTrue(hyperplan_file.is_file())

    @patch('hapycolor.config.input_path',
           return_value=pathlib.Path("./README.md").expanduser())
    @patch('hapycolor.targets.vim_helpers.VimHelpers.bundle_plugins_path',
           side_effect=exceptions.NoCommonPathFound(""))
    def test_vim_file(self, mock_input, mock_bundle_path):
        """ Assert that 'save_vim' fails when a file is provided """
        with self.assertRaises(exceptions.WrongInputError):
            Vim.initialize_config()

    def test_config_sections(self):
        """ Assert that the correct sections exist in the config file """
        import configparser

        configuration = configparser.ConfigParser()
        configuration.read(config.get_default_config())
        expected_sections = ["core", "hyperplan", "Iterm", "Wallpaper",
                             "Filters", "Gnome"]
        self.assertEqual(set(expected_sections), set(configuration.sections()))

    @patch('platform.system', return_value="Windows")
    def test_not_supported_operating_system(self, get_os):
        """ Checks that the 'os' getter works properly when running the program
            on an unsupported platform """
        with self.assertRaises(exceptions.PlatformNotSupportedError):
            config.os()

    @patch('platform.system', side_effect=["Linux", "Darwin"])
    def test_supported_operating_system(self, get_os):
        """ Checks that the 'os' getter works properly when running the program
            on a supported platform """
        try:
            self.assertEqual(config.os(), config.OS.LINUX)
        except exceptions.PlatformNotSupportedError as err:
            self.fail("'os' getter raised error: " + str(err) + " - on a Linux"
                      + " platform")

        try:
            self.assertEqual(config.os(), config.OS.DARWIN)
        except exceptions.PlatformNotSupportedError as err:
            self.fail("'os' getter raised error: " + str(err) + " - on a"
                      + " Darwin platform")

    @helpers.configurationtesting()
    def test_configuration_app_name(self):
        self.assertEqual(config.app_name(), "hapycolor")

    @helpers.configurationtesting()
    @unittest.skipUnless(config.os() == config.OS.DARWIN, "Tests Darwin's"
                         + " environment")
    def test_configuration_iterm_template(self):
        raw_path = Iterm.load_config()[Iterm.template_key]
        iterm_template_path = pathlib.Path(raw_path).resolve()
        self.assertTrue(iterm_template_path.exists())

    @helpers.configurationtesting()
    @unittest.skipUnless(config.os() == config.OS.DARWIN, "Tests Darwin's"
                         + " environment")
    def test_configuration_wallpaper(self):
        raw_path = Wallpaper.load_config()[Wallpaper.configuration_darwin]
        wallpaper_path = pathlib.Path(raw_path).expanduser()
        self.assertTrue(wallpaper_path.exists())

    @helpers.configurationtesting()
    def test_hyperplan_files(self):
        with self.assertRaises(exceptions.UnknownLuminosityFilterTypeError):
            config.hyperplan_file("hue")
        for f in config.Filter:
            self.assertTrue(pathlib.Path(config.hyperplan_file(f)).exists())
