from . import exceptions

import configparser
import enum
import readline
import pathlib
import platform
import shutil

ROOT_DIR = pathlib.Path(__file__).parent
CONFIG = "hapycolor.config"

# To be overwritten if the user wants to use a custom configuration file
LOCAL_DIR = pathlib.Path("~")
LOCAL_CONFIG = CONFIG

def create_config():
    """
    Creates a local configuration from the default one, in the user's base directory
    """
    dst = get_config()
    if not pathlib.Path(dst).is_file():
        shutil.copyfile(get_default_config(), dst)

def get_config():
    return pathlib.Path(LOCAL_DIR / ("." + LOCAL_CONFIG)).expanduser().as_posix()

def get_default_config():
    return (ROOT_DIR / CONFIG).as_posix()

class OS(enum.Enum):
    LINUX  = 0
    DARWIN = 1


def os():
    platform_os = platform.system()
    if platform_os == "Darwin":
        return OS.DARWIN
    elif platform_os == "Linux":
        return OS.LINUX
    else:
        raise exceptions.PlatformNotSupportedError()


def load(section):
    config = configparser.ConfigParser()
    config.read(get_config())
    try:
        return config[section]
    except KeyError as e:
        raise exceptions.InvalidConfigKeyError("Configuration entry not found", e)


def save(section, target_config):
    """
    Save a new entry in the config file.

    :arg section: a string representing a section in the configuration file
    :arg key: a string representing an entry in the given section
    :arg value: the value relative to the key to be added in the project's configuration file
    """
    config = configparser.ConfigParser()
    config.read(get_config())

    try:
        if section not in config:
            config[section] = target_config
        else:
            for key in target_config:
                config[section][key] = str(target_config[key])
    except KeyError as e:
        raise exceptions.InvalidConfigKeyError("Configuration entry not found", e)

    with open(get_config(), "w") as f:
        config.write(f)


def input_path(prompt_str):
    """
    Prompts the user with a string and returns a :class:`pathlib.Path` from the user's
    input:

    :arg prompt_str: the string to display before the user's entry
    """
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(readline.get_completer())
    return pathlib.Path(input(prompt_str)).expanduser()


def load_config(section):
    config = configparser.ConfigParser()
    config.read(get_config())
    return config[section]


def app_name():
    return load_config("core")["app_name"]


def get_keys():
    return ROOT_DIR + load_config("hyerplan")["keys"]


def hyperplan_file(filter_type):
    config = load_config("hyperplan")
    path = ROOT_DIR
    if filter_type == LuminosityFilter.DARK:
        path /= config["dark"]
    elif filter_type == LuminosityFilter.BRIGHT:
        path /= config["bright"]
    elif filter_type == LuminosityFilter.SATURATION:
        path /= config["saturation"]
    else:
        raise exceptions.UnknownLuminosityFilterTypeError("Unknown filter type")
    return path

# ----------------------------Color Filter ---------------------------------- #
class LuminosityFilter(enum.Enum):
    BRIGHT     = 1
    DARK       = 2
    SATURATION = 3
