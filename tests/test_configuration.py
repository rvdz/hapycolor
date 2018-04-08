from hapycolor import config
from hapycolor import exceptions
from hapycolor import targets
from hapycolor.targets.iterm import Iterm
from hapycolor.targets.vim import Vim
from hapycolor.targets.wallpaper import Wallpaper
from tests import helpers
from unittest.mock import patch
import pathlib
import unittest


class TestConfiguration(unittest.TestCase):
    def test_config_sections(self):
        """ Assert that the correct sections exist in the config file """
        import configparser

        configuration = configparser.ConfigParser()
        configuration.read(config.get_default_config())
        expected_sections = ["hyperplan", "Iterm", "Wallpaper", "Gnome"]
        self.assertEqual(set(expected_sections), set(configuration.sections()))
