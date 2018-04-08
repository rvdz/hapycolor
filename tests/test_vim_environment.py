import unittest
from hapycolor.targets.vim_environment import VimEnvironments
from unittest.mock import patch
import re
from hapycolor import exceptions
import subprocess

@unittest.skipIf(not VimEnvironments.is_vim_installed(), "Vim is not installed")
class TestVimEnvironments(unittest.TestCase):
    def test_find_plugin_regex(self):
        res = VimEnvironments.find_plugin("lightline.vim")
        self.assertIsNotNone(res)
        self.assertRegex(res, "^.*/lightline.vim$")

    def test_find_unexistent_plugin(self):
        self.assertIsNone(VimEnvironments.find_plugin("toto.vim"))

    def test_plugin_paths(self):
        try:
            plugins = VimEnvironments.plugin_paths()
            self.assertIsInstance(plugins, list)
        except Exception as exc:
            self.fail(str(exc))
