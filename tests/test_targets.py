from hapycolor import config
from hapycolor import targets
from hapycolor import exceptions
from hapycolor.targets import base, vim, lightline, iterm, wallpaper
from hapycolor.targets import gnome_terminal
from tests import helpers
from unittest.mock import patch
import unittest


class TestTarget(unittest.TestCase):
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

    @patch('hapycolor.targets.os', return_value=targets.OS.LINUX)
    def test_get_compatible_linux(self, mock_os):
        for t in targets.get_compatible():
            self.assertIn(targets.OS.LINUX, t.compatible_os())

    @patch('hapycolor.targets.os', return_value=targets.OS.DARWIN)
    def test_get_compatible_darwin(self, mock_os):
        for t in targets.get_compatible():
            self.assertIn(targets.OS.DARWIN, t.compatible_os())

    def test_reconfigure_valid_target(self):
        try:
            target_str = "vim"
            clazz_str = "".join([t.title() for t in target_str.split("_")])
            clazz = eval(target_str + "." + clazz_str)
            self.assertIsInstance(clazz(), base.Target)
        except Exception as e:
            self.fails(str(e))

    def test_reconfigure_valid_target_module(self):
        with self.assertRaises(NameError):
            target_str = "Vim"
            eval(target_str)

    def test_target_class_names(self):
        """
        Assert that each target class is named after its module name. It should
        be a PascalCase version of it. In addition, it checks also if the
        respective class inherits from :class:base.Target.

        .. note:: When adding a new test, it should be added in the list:
            `targets.__all__`, defined in this test.
        """
        import inspect
        targets.__all__ = ['vim', 'lightline', 'iterm', 'wallpaper',
                           'gnome_terminal']
        target_modules = inspect.getmembers(targets)[1][1]
        for m in target_modules:
            try:
                self.assertTrue(inspect.ismodule(eval("targets." + m)))
                clazz_str = "".join([t.title() for t in m.split("_")])
                clazz = eval(m + "." + clazz_str)
                self.assertTrue(inspect.isclass(clazz))
                self.assertIsInstance(clazz(), base.Target)
            except NameError as e:
                self.fails(str(e))

    @patch('platform.system', return_value="Windows")
    def test_not_supported_operating_system(self, get_os):
        """ Checks that the 'os' getter works properly when running the program
            on an unsupported platform """
        with self.assertRaises(exceptions.PlatformNotSupportedError):
            targets.os()

    @patch('platform.system', side_effect=["Linux", "Darwin"])
    def test_supported_operating_system(self, get_os):
        """ Checks that the 'os' getter works properly when running the program
            on a supported platform """
        try:
            self.assertEqual(targets.os(), targets.OS.LINUX)
        except exceptions.PlatformNotSupportedError as err:
            self.fail("'os' getter raised error: " + str(err) + " - on a Linux"
                      + " platform")

        try:
            self.assertEqual(targets.os(), targets.OS.DARWIN)
        except exceptions.PlatformNotSupportedError as err:
            self.fail("'os' getter raised error: " + str(err) + " - on a"
                      + " Darwin platform")
