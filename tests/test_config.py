from hapycolor import config

import pathlib
import unittest
from unittest.mock import patch

class ConifgTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_hypeplans_files_exist(self):
        """ Checks if manual hyperplan point's file exists """
        for filter_type in config.Filter:
            self.assertTrue(pathlib.Path(config.hyperplan_file(filter_type)).is_file())

    @patch('hapycolor.config.input_path', return_value=pathlib.Path("./README.md").expanduser())
    def test_vim_file(self, input):
        """ Assert that 'save_vim' fails when a file is provided """
        with self.assertRaises(NotImplementedError):
            config.save_vim()

    @patch('hapycolor.config.input_path', return_value=pathlib.Path("~").expanduser())
    def test_iterm_fail_with_directory(self, input):
        """ Assert that 'save_iterm' fails when a directory is provided """
        with self.assertRaises(NotImplementedError):
            config.save_iterm()

    @patch('hapycolor.config.input_path', return_value=pathlib.Path("./com.googlecode.iterm2.plist").expanduser())
    def test_iterm_fail_with_incorrect_file_1(self, input):
        """ Assert that 'save_iterm' fails when an unexisting file is provided """
        with self.assertRaises(NotImplementedError):
            config.save_iterm()

    @patch('hapycolor.config.input_path', return_value=pathlib.Path("./README.md").expanduser())
    def test_iterm_fail_with_incorrect_file_2(self, input):
        """ Assert that 'save_iterm' fails when an unexisting file is provided """
        with self.assertRaises(NotImplementedError):
            config.save_iterm()


    # This test could be removed if the Feature dictionnaries were correctly typed
    def test_features(self):
        """ Assert that the Feature enum is correctly defined """
        import types

        keys = ["name", "os", "save", "export", "key"]
        for e in config.Feature:
            for k in keys:
                self.assertTrue(k in e.value)
                if k == "os":
                    self.assertTrue(e.value[k] in config.OS)
                if k == "save" or k == "export":
                    self.assertTrue(type(e.value[k]) == types.FunctionType \
                                        or e.value[k] == NotImplemented)
                if k == "key":
                    self.assertTrue(type(e.value[k]) == str)


    def test_config_sections(self):
        """ Assert that the correct sections exist in the config file """
        import configparser

        configuration = configparser.ConfigParser()
        configuration.read(config.project_config)
        expected_sections = ["core", "export", "reducer", "hyperplan"]
        self.assertTrue(set(expected_sections) == set(configuration.sections()))
