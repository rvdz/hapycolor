import unittest
from unittest import mock
from hapycolor.targets import yabar
from hapycolor import palette

class TestYabar(unittest.TestCase):

    mock_dict = {yabar.Yabar.configuration_key: None}

    @mock.patch("hapycolor.targets.yabar.Yabar.load_config",
                return_value=mock_dict)
    def test_export(self, mock_dict):
        configuration = """
    overline-size: 2;
    slack-size: 12;

    window: {
            exec: "~/.config/yabar/scripts/icon_workspace.py";
            align: "left";
            fixed-size: 30;
    type: "persist";
            // @hapycolor("random")
            underline-color-rgb:0x4E52BF;
    }
        """
        pltte = palette.Palette()
        pltte.colors = [(1, 2, 3)]
        expected = configuration.replace("0x4E52BF", "0x010203")

        mock_open = mock.mock_open(read_data=configuration)
        with mock.patch("builtins.open", mock_open):
            yabar.Yabar.export(pltte, "path/to/image")
        mock_open().write.assert_called_once_with(expected)
