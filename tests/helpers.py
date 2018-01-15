from hapycolor import config
from hapycolor import palette
from unittest import mock
import contextlib
import os
import shutil


@contextlib.contextmanager
def disableprints():
    with mock.patch('hapycolor.visual.print_palette'), \
            mock.patch('builtins.print'):
        yield


def mock_get_config():
    return (config.ROOT_DIR / ("../tests/" + config.CONFIG)).as_posix()


@contextlib.contextmanager
def configurationtesting():
    """
    Copy configuration file into tests folder before starting the configuration
    tests, and suppresses it after correct termination. In addition, the new
    configuration will be used by all functions accessing the configuration
    getter, instead of the normal located in the main project's module. In a
    nutshell, when the instructions in this contexts will perform operations on
    the configuration file, the original file will be left unaltered, and
    instead, a new configuration file located in the 'tests' folder will
    become the target.
    """
    shutil.copyfile(config.get_default_config(), mock_get_config())
    with mock.patch('hapycolor.config.get_config', mock_get_config):
        yield
    os.remove(mock_get_config())


@contextlib.contextmanager
def retrytesting(retries=0):
    return_values = [True] * retries + [False]
    with mock.patch('hapycolor.targets.retry', side_effect=return_values):
        yield


def generate_palette(size):
    pltte = palette.Palette()
    pltte.foreground = (0, 0, 0)
    pltte.background = (0, 0, 0)
    pltte.colors = [(c, c, c) for c in range(size)]
    return pltte
