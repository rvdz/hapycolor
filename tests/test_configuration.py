from hapycolor import config
from shutil import copyfile, rmtree
from unittest.mock import patch
from hapycolor import exceptions

import contextlib
import os
import pathlib
import unittest


class TestConfiguration(unittest.TestCase):
    def setUp(self):
        pass

    def test_hypeplans_files_exist(self):
        """ Checks if manual hyperplan point's file exists """
        for filter_type in config.Filter:
            self.assertTrue(pathlib.Path(config.hyperplan_file(filter_type)).is_file())

    @patch('hapycolor.config.input_path', return_value=pathlib.Path("./README.md").expanduser())
    def test_vim_file(self, input):
        """ Assert that 'save_vim' fails when a file is provided """
        with self.assertRaises(exceptions.WrongInputError):
            config.save_vim()

    @patch('hapycolor.config.input_path', return_value=pathlib.Path("~").expanduser())
    def test_iterm_fail_with_directory(self, input):
        """ Assert that 'save_iterm' fails when a directory is provided """
        with self.assertRaises(exceptions.WrongInputError):
            config.save_iterm()

    @patch('hapycolor.config.input_path', return_value=pathlib.Path("./com.googlecode.iterm2.plist").expanduser())
    def test_iterm_fail_with_incorrect_file_1(self, input):
        """ Assert that 'save_iterm' fails when an unexisting file is provided """
        with self.assertRaises(exceptions.WrongInputError):
            config.save_iterm()

    @patch('hapycolor.config.input_path', return_value=pathlib.Path("./README.md").expanduser())
    def test_iterm_fail_with_incorrect_file_2(self, input):
        """ Assert that 'save_iterm' fails when an unexisting file is provided """
        with self.assertRaises(exceptions.WrongInputError):
            config.save_iterm()


    # This test could be removed if the Target dictionnaries were correctly typed
    def test_features(self):
        """ Assert that the Target enum is correctly defined """
        import types

        keys = ["name", "os", "save", "export", "key"]
        for e in config.Target:
            for k in keys:
                self.assertIn(k, e.value)
                if k == "os":
                    self.assertTrue(all([(os in config.OS) for os in e.value[k]]))
                if k == "save" or k == "export":
                    self.assertTrue(type(e.value[k]) == types.FunctionType \
                                        or e.value[k] == None or e.value[k] == NotImplemented)
                if k == "key":
                    self.assertIsInstance(e.value[k], str)


    def test_config_sections(self):
        """ Assert that the correct sections exist in the config file """
        import configparser

        configuration = configparser.ConfigParser()
        configuration.read(config.get_config())
        expected_sections = ["core", "export", "reducer", "hyperplan"]
        self.assertEqual(set(expected_sections), set(configuration.sections()))

    mock_library = {"source"   : "./color/reducer.cpp",
                    "library"  : "../tests/lib_reducer",
                    "compiler" : "g++",
                    "options"  : "-std=c++11 -O3"}

    @patch('hapycolor.config.load_config', return_value=mock_library)
    def test_reduce_library_compilation(self, get_library):
        """ Tests the library's compilation on the current platform """
        import os
        library = config.get_reduce_library()
        with self.assertRaises(AttributeError):
            library.foo
        self.assertTrue(callable(library.reduce))

        library_path = config.ROOT_DIR + "/" + get_library()["library"]
        if config.os() == config.OS.DARWIN:
            library_path = library_path + ".dylib"
        elif config.os() == config.OS.LINUX:
            library_path = library_path + ".so"

        self.assertTrue(pathlib.Path(library_path).resolve().exists())
        os.remove(library_path)

    @patch('platform.system', return_value="Windows")
    def test_not_supported_operating_system(self, get_os):
        """ Checks that the 'os' getter works properly when running the program
            on an unsupported platform """
        with self.assertRaises(exceptions.PlatformNotSupportedError):
            config.os()

    @patch('platform.system', side_effect=["Linux", "Darwin"])
    def test_not_supported_operating_system(self, get_os):
        """ Checks that the 'os' getter works properly when running the program
            on a supported platform """
        try:
            self.assertEqual(config.os(), config.OS.LINUX)
        except exceptions.PlatformNotSupportedError as err:
            self.fail("'os' getter raised error: " + str(err) + " - on a Linux platform")

        try:
            self.assertEqual(config.os(), config.OS.DARWIN)
        except exceptions.PlatformNotSupportedError as err:
            self.fail("'os' getter raised error: " + str(err) + " - on a Darwin platform")

    def test_configuration_app_name(self):
        self.assertEqual(config.app_name(), "hapycolor")

    @unittest.skipUnless(config.os() == config.OS.DARWIN, "requires macOs")
    def test_configuration_iterm_template(self):
        iterm_template_path = pathlib.Path(config.iterm_template()).resolve()
        self.assertTrue(iterm_template_path.exists())

    @unittest.skipUnless(config.os() == config.OS.DARWIN, "requires macOs")
    def test_configuration_wallpaper(self):
        wallpaper_path = pathlib.Path(config.wallpaper_config()).expanduser()
        self.assertTrue(wallpaper_path.exists())

    def test_hyperplan_files(self):
        with self.assertRaises(exceptions.UnknownFilterTypeError):
            config.hyperplan_file("hue")
        for f in config.Filter:
            self.assertTrue(pathlib.Path(config.hyperplan_file(f)).exists())

    from collections import defaultdict
    @patch('hapycolor.config.load_config', return_value=defaultdict(lambda: str(True)))
    def test_target_export_functions(self, mock_config_dict):
        """ Checks that the target's export functions are callable """
        with patch('hapycolor.config.os', return_value=config.OS.LINUX):
            for f in config.get_export_functions():
                self.assertTrue(callable(f))
        with patch('hapycolor.config.os', return_value=config.OS.DARWIN):
            for f in config.get_export_functions():
                self.assertTrue(callable(f))

def mock_get_config():
    return config.ROOT_DIR + "/../tests/config.ini"

@contextlib.contextmanager
def configurationtesting():
    """ Copy configuration file into tests folder before starting the configuration tests,
        and suppresses it after correct termination. In addition, the new configuration
        will be used by all functions accessing the configuration getter, instead of the
        normal located in the main project's module. In a nutshell, when the instructions in this
        contexts will perform operations on the configuration file, the original file will be left
        unaltered, and instead, a new configuration file located in the 'tests' folder will become
        the target. """
    copyfile(config.get_config(), mock_get_config())
    with patch('hapycolor.config.get_config', mock_get_config):
        yield
    os.remove(mock_get_config())

class IntegrationTest(unittest.TestCase):
    def setUp(self):
        pass

    def __test_configuration_initialization_targets_enabled(self, data, os):
        """ Testing the configuration initialization when all the targets of a
            given operating system are disabled """
        config.initialize()
        target_config = config.load_config("export")
        for t in config.Target:
            if config.os() in t.value["os"]:
                self.assertTrue(target_config[t.value["enabled"]] == str(True))
            else:
                self.assertTrue(t.value["enabled"] not in target_config)

        for t in config.Target:
            if config.os() in t.value["os"] and t.value["key"]:
                self.assertTrue(t.value["key"] in target_config)

    def __test_configuration_initialization_target_diabled(self, data, os):
        """ Testing the configuration initialization when all the targets of a
            given operating system are disabled """
        config.initialize()
        target_config = config.load_config("export")
        for t in config.Target:
            if config.os() in t.value["os"]:
                self.assertTrue(target_config[t.value["enabled"]] == str(False))
            else:
                self.assertTrue(t.value["enabled"] not in target_config)


    @patch('builtins.input', side_effect=["y", "./tests", "y", "./tests/com.googlecode.iterm2.plist", "y"])
    @patch('hapycolor.config.os', return_value=config.OS.DARWIN)
    @configurationtesting()
    def test_config_initialization_macos_target_enabled(self, input, os):
        """ Testing the configuration initialization when all the targets compatible
            with macOs are enabled """
        self.__test_configuration_initialization_targets_enabled(input, os)


    @patch('builtins.input', side_effect=["n", "n", "n"])
    @patch('hapycolor.config.os', return_value=config.OS.DARWIN)
    @configurationtesting()
    def test_config_initialization_linux_target_disabled(self, input, os):
        """ Testing the configuration initialization when all the targets compatible
            with macOs are disabled """
        self.__test_configuration_initialization_target_diabled(input, os)


    @patch('builtins.input', side_effect=["y", "./tests"])
    @patch('hapycolor.config.os', return_value=config.OS.LINUX)
    @configurationtesting()
    def test_config_initialization_linux_targets_enabled(self, input, os):
        """ Testing the configuration initialization when all the targets compatible
            with linux are enabled """
        self.__test_configuration_initialization_targets_enabled(input, os)


    @patch('builtins.input', side_effect=["n"])
    @patch('hapycolor.config.os', return_value=config.OS.LINUX)
    @configurationtesting()
    def test_config_initialization_linux_target_disabled(self, input, os):
        """ Testing the configuration initialization when all the targets compatible
            with linux are disabled """
        self.__test_configuration_initialization_target_diabled(input, os)

    @patch.dict('hapycolor.config.Target.ITERM.value', {"save" : 3})
    @patch.dict('hapycolor.config.Target.VIM.value', {"save" : 3})
    @configurationtesting()
    def test_target_save_attribute_not_function(self):
        """ Tests that the configuration saving function is callable """
        with patch('hapycolor.config.os', return_value=config.OS.DARWIN):
            with self.assertRaises(TypeError):
                config.initialize_target(config.Target.ITERM, is_enabled=True)
        with patch('hapycolor.config.os', return_value=config.OS.LINUX):
            with self.assertRaises(TypeError):
                config.initialize_target(config.Target.VIM, is_enabled=True)
