from hapycolor import helpers
from hapycolor import config
from hapycolor import __main__

import pathlib
import unittest
from unittest.mock import patch

class TestMain(unittest.TestCase):
    @patch('hapycolor.__main__.parse_arguments', return_value={"file":"../tests/images/taipei.jpg"})
    @patch('hapycolor.config.get_export_functions', return_value=[])
    @patch('hapycolor.color.extractor.Extractor')
    @patch('hapycolor.config.initialize')
    @patch('hapycolor.visual.print_palette')
    @patch('hapycolor.helpers.save_json')
    @patch('hapycolor.__main__.colors_to_file')
    @patch('builtins.print')
    def test_argument_parsing(self, mock_arg_parse, mock_export, mock_extrct, mock_init, \
                                mock_print_palette, mock_save, mock_colors_to_file, mock_print):
        __main__.main()
