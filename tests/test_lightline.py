"""
Lightline test module
"""
import enum
import contextlib
import pathlib
import unittest
from unittest import mock
from tests.helpers import disableprints
from hapycolor.targets.lightline import Lightline


class TestLightline(unittest.TestCase):

    @unittest.skipUnless(pathlib.Path("~/.vim/pack/bundle/start/lightline.vim")
        .expanduser().is_dir(), "This test requires vim's plugins to be "
        + "located in this folder: '~/vim/pack/bundle/start")
    def test_select_colorscheme_path(self):
        path = Lightline.select_colorscheme_path()
        expected = "~/.vim/pack/bundle/start/lightline.vim/autoload/lightline" \
                    + "/colorscheme/hapycolor.vim"
        self.assertEqual(path, pathlib.Path(expected).expanduser().as_posix())

    def test_add_colors_one_mode(self):
        mock_theme = ["line 1", "some text $NORMAL some other text", "line 3"]
        # colors = [NORMAL, INSERT, REPLACE, VISUAL]
        mock_palette = mock.Mock()
        mock_palette.colors = [(1, 5, 9), (78, 89, 100), (23, 45, 56), (200, 250, 100)]
        mock_palette.foreground = (255, 255, 255)
        mock_palette.background = (0, 0, 0)

        expected = ["line 1", "some text '#172d38', 17 some other text", "line 3"]

        result = Lightline.add_colors(mock_theme, mock_palette)

        self.assertEqual(result, expected)

    def test_add_colors_all_modes(self):
        mock_palette = mock.Mock()
        # colors = [NORMAL, INSERT, REPLACE, VISUAL]
        mock_palette.colors = [(1, 5, 9), (9, 6, 5), (23, 45, 56),
                               (200, 250, 100)]
        mock_palette.foreground = (255, 255, 255)
        mock_palette.background = (0, 0, 0)

        mock_theme = ["line 1 [ $INSERT ] end line 1",
                      "some text $NORMAL some other text",
                      "$VISUAL line 3", "line 4 $REPLACE"]

        expected = ["line 1 [ '#090605', 16 ] end line 1",
                    "some text '#c8fa64', 191 some other text",
                    "'#172d38', 17 line 3",
                    "line 4 '#010509', 16"]

        result = Lightline.add_colors(mock_theme, mock_palette)
        self.assertEqual(result, expected)

    def test_themes_finder(self):
        lightline_file = "hapycolor/targets/lightline/__init__.py"
        lightline_dir = pathlib.Path(lightline_file).parent
        lightline_files = [t for t in lightline_dir.iterdir() if ".vim" == t.suffix]
        ThemeEnum = enum.Enum("ThemeEnum", [(t.stem.upper(), t.as_posix())
                                            for t in lightline_files])

        self.assertIn("hapycolor/targets/lightline/landscape.vim", [t.value for t in ThemeEnum])
        self.assertNotIn("hapycolor/targets/lightling/__init__.py", [t.value for t in ThemeEnum])
