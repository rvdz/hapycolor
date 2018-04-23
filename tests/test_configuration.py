from hapycolor import config
import os
import contextlib
import unittest
from unittest import mock


class TestConfiguration(unittest.TestCase):
    def test_config_sections(self):
        """ Assert that the correct sections exist in the config file """
        import configparser

        configuration = configparser.ConfigParser()
        configuration.read(config.get_default_config())
        expected_sections = ["hyperplan", "Iterm", "Wallpaper", "Gnome"]
        self.assertEqual(set(expected_sections), set(configuration.sections()))
