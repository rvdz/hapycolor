from hapycolor import exceptions
from hapycolor.targets.rofi import Rofi

from unittest.mock import MagicMock
from unittest.mock import patch

import pathlib
import tests.helpers
import unittest


class TestI3(unittest.TestCase):

    @tests.helpers.configurationtesting()
    @patch("hapycolor.helpers.input_path", MagicMock(side_effect=
           [pathlib.Path("./tests"), pathlib.Path("./setup.py")]))
    def test_initialize_config_ok(self):
        Rofi.initialize_config()
        expected = {Rofi.template_key: "setup.py",
                    Rofi.configuration_key: "tests"}
        self.assertDictEqual(expected, Rofi.load_config())

    @tests.helpers.configurationtesting()
    @patch("hapycolor.helpers.input_path", MagicMock(side_effect=
           [pathlib.Path("./tests"), pathlib.Path("./yolo.py")]))
    def test_initialize_config_template_fail(self):
        with self.assertRaises(exceptions.WrongInputError):
            Rofi.initialize_config()

    def test_is_config_initialized_default(self):
        self.assertFalse(Rofi.is_config_initialized())
