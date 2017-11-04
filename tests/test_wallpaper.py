from hapycolor import config
from hapycolor.targets.wallpaper import Wallpaper
from hapycolor import exceptions

from unittest.mock import patch

import unittest

class TestWallpaper(unittest.TestCase):
    @unittest.skipUnless(config.os() == config.OS.DARWIN, "targetted platform: Darwin")
    @patch('hapycolor.targets.wallpaper.Wallpaper.load_config', return_value={Wallpaper.configuration_key : '~'})
    def test_incorrect_configuration_file(self, get_config):
        with self.assertRaises(exceptions.ExportTargetFailure):
            Wallpaper.export({}, "name")

    @unittest.skipUnless(config.os() == config.OS.DARWIN, "targetted platform: Darwin")
    @patch('subprocess.call', lambda x: x)
    def test_configuration_file_exist(self):
        try:
            Wallpaper.export({}, "name")
        except Exception as err:
            self.fail(str(err))
