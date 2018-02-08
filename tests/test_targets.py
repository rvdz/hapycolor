from hapycolor import config, exceptions, targets
from hapycolor.targets import base, vim, lightline, iterm, wallpaper
from tests import helpers
from unittest.mock import patch
import unittest


class TestTargets(unittest.TestCase):
    def test_target_compatible_os_implemented(self):
        for t in targets.get():
            try:
                t.compatible_os()
            except Exception as e:
                self.fail(str(e))

    @helpers.configurationtesting()
    def test_target_is_initialized_implemented(self):
        for t in targets.get():
            try:
                t.is_config_initialized()
            except Exception as e:
                self.fail(str(e))

    @patch('hapycolor.config.os', return_value=config.OS.LINUX)
    def test_get_compatible_linux(self, mock_os):
        for t in targets.get_compatible():
            self.assertIn(config.OS.LINUX, t.compatible_os())

    @patch('hapycolor.config.os', return_value=config.OS.DARWIN)
    def test_get_compatible_darwin(self, mock_os):
        for t in targets.get_compatible():
            self.assertIn(config.OS.DARWIN, t.compatible_os())

    def test_get_valid_module(self):
        try:
            clazz = targets.get_class("vim")
            self.assertIsInstance(clazz(), base.Target)
        except Exception as e:
            self.fails(str(e))

    def test_get_invalid_module(self):
        with self.assertRaises(exceptions.InvalidTarget):
            targets.get_class("Vim")

        with self.assertRaises(exceptions.InvalidTarget):
            targets.get_class("__doc__")

    def test_target_class_names(self):
        """
        Assert that each target class is named after its module name. It should
        be a PascalCase version of it. In addition, it checks also if the
        respective class inherits from :class:base.Target.

        .. note:: When adding a new test, it should be added in the list:
            `targets.__all__`, defined in this test.
        """
        import inspect
        targets.__all__ = ['vim', 'lightline', 'iterm', 'wallpaper']
        target_modules = inspect.getmembers(targets)[0][1]
        for m in target_modules:
            try:
                self.assertTrue(inspect.ismodule(eval("targets." + m)))
                clazz_str = "".join([t.title() for t in m.split("_")])
                clazz = eval(m + "." + clazz_str)
                self.assertTrue(inspect.isclass(clazz))
                self.assertIsInstance(clazz(), base.Target)
            except NameError as e:
                self.fails(str(e))
