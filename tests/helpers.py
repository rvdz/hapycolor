from hapycolor import config
from hapycolor import palette
from hapycolor.targets.iterm import Iterm
from hapycolor.targets.vim import Vim
import shutil
from unittest import mock
import contextlib
import os
import pathlib

@contextlib.contextmanager
def disableprints():
    with mock.patch('hapycolor.visual.print_palette') as mock_print_palette, \
            mock.patch('builtins.print') as mock_print:
        yield


def mock_get_config():
    return config.ROOT_DIR + "/../tests/config.ini"


@contextlib.contextmanager
def configurationtesting():
    """
    Copy configuration file into tests folder before starting the configuration tests,
    and suppresses it after correct termination. In addition, the new configuration
    will be used by all functions accessing the configuration getter, instead of the
    normal located in the main project's module. In a nutshell, when the instructions in this
    contexts will perform operations on the configuration file, the original file will be left
    unaltered, and instead, a new configuration file located in the 'tests' folder will become
    the target.
    """
    shutil.copyfile(config.get_config(), mock_get_config())
    with mock.patch('hapycolor.config.get_config', mock_get_config):
        yield
    os.remove(mock_get_config())


@contextlib.contextmanager
def itermtesting(fails=0):
    valid_entry = ["./tests/com.googlecode.iterm2.plist"]
    invalid_entry = ["."]
    entries = invalid_entry * fails + valid_entry

    test_config_path= config.ROOT_DIR + "/../tests/com.googlecode.iterm2.plist"
    tmp_test_config_path= config.ROOT_DIR + "/../tests/com.googlecode.iterm2.tmp"
    shutil.copyfile(test_config_path, tmp_test_config_path)
    mock_config_dict = {Iterm.preferences_key : tmp_test_config_path,
                        Iterm.template_key    : Iterm.load_config()[Iterm.template_key]}

    with mock.patch('hapycolor.targets.iterm.Iterm.load_config', return_value=mock_config_dict):
        with mock.patch('builtins.input', side_effect=entries):
            yield
    os.remove(tmp_test_config_path)


@contextlib.contextmanager
def vimtesting(fails=0):
    valid_entry = ["./tests"]
    invalid_entry = ["./tests/run_suite.py"]
    entries = invalid_entry * fails + valid_entry
    with mock.patch('builtins.input', side_effect=entries):
        yield
    if pathlib.Path("./tests/hapycolor").exists():
        shutil.rmtree("./tests/hapycolor")


@contextlib.contextmanager
def retrytesting(retries=0):
    return_values = [True] * retries + [False]
    with mock.patch('hapycolor.targets.retry', side_effect=return_values):
        yield


def generate_palette(size):
    pltte = palette.Palette()
    pltte.foreground = (0,0,0)
    pltte.background = (0,0,0)
    pltte.colors = [(c,c,c) for c in range(size)]
    return pltte
