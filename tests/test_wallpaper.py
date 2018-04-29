from hapycolor import targets
from hapycolor import exceptions
from hapycolor.targets.wallpaper import Wallpaper
from tests import helpers
from unittest.mock import patch
import pathlib
import unittest


class TestWallpaper(unittest.TestCase):
    @unittest.skipUnless(targets.os() == targets.OS.DARWIN,
                         "targetted platform: Darwin")
    @patch('hapycolor.targets.wallpaper.Wallpaper.load_config',
           return_value={Wallpaper.configuration_darwin: '~'})
    @helpers.configurationtesting()
    def test_incorrect_configuration_file(self, get_config):
        with self.assertRaises(exceptions.ExportTargetFailure):
            Wallpaper.export({}, "name")

    @helpers.configurationtesting()
    @unittest.skipUnless(targets.os() == targets.OS.DARWIN, "Tests Darwin's"
                         + " environment")
    def test_configuration_wallpaper(self):
        raw_path = Wallpaper.load_config()[Wallpaper.configuration_darwin]
        wallpaper_path = pathlib.Path(raw_path).expanduser()
        self.assertTrue(wallpaper_path.exists())
