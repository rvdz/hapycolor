from hapycolor import targets
from hapycolor import exceptions
from hapycolor.targets.wallpaper import Wallpaper
from tests import helpers
from unittest.mock import patch
import pathlib
import unittest


class TestWallpaper(unittest.TestCase):
    @helpers.configurationtesting()
    def test_invalid_image_path(self):
        with self.assertRaises(exceptions.WrongInputError):
            Wallpaper.export({}, "name")

    @helpers.configurationtesting()
    @unittest.skipUnless(targets.os() == targets.OS.DARWIN, "Tests Darwin's"
                         + " environment")
    def test_configuration_wallpaper(self):
        raw_path = Wallpaper.load_config()[Wallpaper.configuration_darwin]
        wallpaper_path = pathlib.Path(raw_path).expanduser()
        self.assertTrue(wallpaper_path.exists())

    @helpers.configurationtesting()
    @unittest.skipUnless(targets.os() == targets.OS.DARWIN,
                         "targetted platform: Darwin")
    @patch('subprocess.run')
    def test_export(self, mock_subprocess):
        try:
            Wallpaper.export({}, "images/firewatch.jpg")
        except Exception as err:
            self.fail(str(err))
