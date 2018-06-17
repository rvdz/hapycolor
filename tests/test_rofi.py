from hapycolor import exceptions
from hapycolor.targets.rofi import Rofi

from unittest.mock import MagicMock
from unittest.mock import patch

import pathlib
import tests.helpers
import unittest


class TestRofi(unittest.TestCase):
    def test_themes_finder(self):
        self.assertIn("hapycolor/targets/rofi/Monokai.rasi", [t.value for t in Rofi.ThemeEnum])
        self.assertNotIn("hapycolor/targets/rofi/__init__.py", [t.value for t in Rofi.ThemeEnum])
