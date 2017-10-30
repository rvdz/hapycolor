from hapycolor import config
from hapycolor.export import wallpaper
from hapycolor import exceptions

from unittest.mock import patch

import unittest

class TestWallpaper(unittest.TestCase):
    @unittest.skipUnless(config.os() == config.OS.DARWIN, "targetted platform: Darwin")
    @patch('hapycolor.config.wallpaper_config', return_value='~')
    def test_incorrect_configuration_file(self, get_config):
        with self.assertRaises(exceptions.ExportTargetFailure):
            wallpaper.Wallpaper.set_macos({}, "name", "image")

    @unittest.skipUnless(config.os() == config.OS.DARWIN, "targetted platform: Darwin")
    @patch('subprocess.call', lambda x: x)
    def test_configuration_file_exist(self):
        try:
            wallpaper.Wallpaper.set_macos({}, "name", "image")
        except Exception as err:
            self.fail(str(err))
