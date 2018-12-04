import enum
import pathlib
import tests.helpers
import unittest


class TestRofi(unittest.TestCase):
    def test_themes_finder(self):
        rofi_file = "hapycolor/targets/rofi/__init__.py"
        rofi_dir = pathlib.Path(rofi_file).parent
        rasi_files = [t for t in rofi_dir.iterdir() if ".rasi" == t.suffix]
        ThemeEnum = enum.Enum("ThemeEnum",
                              [(t.stem.upper(), t.as_posix())
                               for t in rasi_files])

        self.assertIn("hapycolor/targets/rofi/Monokai.rasi", [t.value for t in ThemeEnum])
        self.assertNotIn("hapycolor/targets/rofi/__init__.py", [t.value for t in ThemeEnum])
