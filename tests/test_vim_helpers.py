import unittest
from hapycolor.targets.vim_helpers import VimHelpers
from unittest.mock import patch
from hapycolor import exceptions
import subprocess

@unittest.skipIf(not VimHelpers.is_vim_installed(), "Vim is not installed")
class TestVimHelpers(unittest.TestCase):
    def test_find_plugin_regex(self):
        res = VimHelpers.find_plugin("lightline.vim")
        self.assertRegex(res.resolve().as_posix(), "lightline.vim")

    def test_find_unexistent_plugin(self):
        with self.assertRaises(exceptions.PluginError):
            VimHelpers.find_plugin("toto.vim")
