import unittest
from hapycolor import config
from unittest.mock import patch
from hapycolor import targets
from tests import helpers

class TestTarget(unittest.TestCase):

    def test_target_compatible_os_implemented(self):
        for t in targets.get():
            try:
                t.compatible_os()
            except Exception as e:
                self.fail(str(e))

    def test_target_is_initialized_implemented(self):
        for t in targets.get():
            try:
                t.is_config_initialized()
            except Exception as e:
                self.fail(str(e))


    @patch('hapycolor.config.os', return_value=config.OS.LINUX)
    def test_get_compatible_linux(self, mock_os):
        for t in targets.get_compatible():
            self.assertIn(config.OS.LINUX, t.compatible_os())

    @patch('hapycolor.config.os', return_value=config.OS.DARWIN)
    def test_get_compatible_darwin(self, mock_os):
        for t in targets.get_compatible():
            self.assertIn(config.OS.DARWIN, t.compatible_os())
