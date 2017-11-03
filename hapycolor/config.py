from .export import iterm
from .export import vim
from .export import wallpaper
from . import exceptions

import configparser
import ctypes
import enum
import readline
import pathlib
import platform
import subprocess
import os.path
import os.path as pth

# ------------------------- Initialize Config ------------------------------- #

ROOT_DIR = pth.dirname(pth.abspath(__file__))


def get_config():
    return ROOT_DIR + "/config.ini"


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


def input_path(prompt_str):
    """
    Prompts the user with a string and returns a 'pathlib.Path' from the user's
    input:

    Keyword arguments:
    prompt_str -- the string to display before the user's entry
    """
    return pathlib.Path(input(prompt_str)).expanduser()


def save_vim():
    """
    Creates the path where the colorscheme will be generated, and stores it in
    the project's configuration file.
    """
    p = input_path("Path to vim's custom plugins directory: ")
    if not p.is_absolute():
        p = p.resolve()

    if not p.is_dir():
        raise exceptions.WrongInputError("Must be a directory")

    p = p / "hapycolor" / "colors"
    if not p.exists():
        p.mkdir(parents=True)
    vim_key = Target.VIM.value["key"]
    save_config("export", vim_key, (p / "hapycolor.vim").as_posix())


def save_iterm():
    """
    Checks if iTerm's preferences file is correct and save it's path in the
    project configuration file.
    """
    p = input_path("Path to iTerm configuration file: ")
    if not p.is_absolute() and p.is_file():
        p = p.resolve()
    if not p.is_file():
        raise exceptions.WrongInputError("Path does not lead to a file")
    if p.name != "com.googlecode.iterm2.plist":
        raise exceptions.WrongInputError("The file does not match an iTerm"
                                         + " configuration file")
    save_config("export", Target.ITERM.value["key"], p.as_posix())


def save_config(section, key, value):
    """
    Save a new entry in the config file.

    Keyword arguments:
    section -- a string representing a section in the configuration file
    key -- a string representing an entry in the given section
    value -- the value relative to the key to be added in the project's
             configuration file
    """
    config = configparser.ConfigParser()
    config.read(get_config())
    try:
        config[section][key] = value
    except KeyError as e:
        raise exceptions.InvalidConfigKey("Configuration entry not found", e)

    with open(get_config(), "w") as f:
        config.write(f)


# TODO: Reimplement with better typing
class Target(enum.Enum):
    """ Links each target with its:
            - name
            - system compatibility
            - configuration save function
            - export function
            - boolean indicating if the target has been enabled
            - configuration value's key
                                    """
    VIM            = {"name"     : "Vim",
                      "os"       : [OS.LINUX, OS.DARWIN],
                      "save"     : save_vim,
                      "export"   : vim.Vim.profile,
                      "enabled"  : "vim_enabled",
                      "key"      : "colorscheme_vim"}

    ITERM          = {"name"     : "iTerm",
                      "os"       : [OS.DARWIN],
                      "save"     : save_iterm,
                      "export"   : iterm.Iterm.profile,
                      "enabled"  : "iterm_enabled",
                      "key"      : "iterm_config"}

    WALLPAPER      = {"name"     : "Wallpaper",
                      "os"       : [OS.DARWIN],
                      "save"     : None,
                      "export"   : wallpaper.Wallpaper.set_macos,
                      "enabled"  : "wallpaper_enabled",
                      "key"      : "wallpaper_macos"}


def initialize():
    """
    Intializes the targets' configurations that are compatible and not disabled
    """
    config = load_config("export")

    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(readline.get_completer())

    # Filters undefined compatible targets which have not been disabled
    f = lambda x: os() in x.value["os"] \
        and (x.value["enabled"] not in config)

    for t in filter(f, Target):
        res = input("Enable " + t.value["name"] + "? (y/n) :")
        if res.capitalize() == "Y":
            initialize_target(t)
        else:
            save_config("export", t.value["enabled"], str(False))


def initialize_target(target):
    """
    Initializes a given target. If the intialization is successful, i.e. the
    user entered a correct information, then, the target's section 'enabled' of
    the configuration file will be saved as 'True', in addition of saving other
    possible data. Else, the former section will be marked as 'False'.

    Keyword arguments:
    target -- one of the enumerates of the class Target
    """
    is_enabled = True
    while target.value["save"] and is_enabled:
        try:
            target.value["save"]()
        except exceptions.WrongInputError as e:
            print(e.msg)
        else:
            break
        if input("\nAbort? (y/n): ").capitalize() == "Y":
            is_enabled = False
    save_config("export", target.value["enabled"], str(is_enabled))


# --------------------------- Access Config --------------------------------- #
def app_name():
    return load_config("core")["app_name"]


def vim():
    return load_config("export")["colorscheme_vim"]


def load_config(section):
    config = configparser.ConfigParser()
    config.read(get_config())
    return config[section]


def get_keys():
    return ROOT_DIR + load_config("hyerplan")["keys"]


def iterm_template():
    return ROOT_DIR + "/" + load_config("export")["iterm_template"]


def iterm_config():
    return load_config("export")[Target.ITERM.value["key"]]


def wallpaper_config():
    return load_config("export")[Target.WALLPAPER.value["key"]]


def hyperplan_file(filter_type):
    config = load_config("hyperplan")
    path = ROOT_DIR + "/"
    if filter_type == Filter.DARK:
        path += config["dark"]
    elif filter_type == Filter.BRIGHT:
        path += config["bright"]
    elif filter_type == Filter.SATURATION:
        path += config["saturation"]
    else:
        raise exceptions.UnknownFilterTypeError("Unknown filter type")
    return path


def get_export_functions():
    """
    Returns a list of functions representing the export functions of the
    enabled targets.
    """
    target_config = load_config("export")
    enabled_t = lambda x: (os() in x.value["os"]) \
        and (target_config[x.value["enabled"]] == "True")
    return [lambda t: t.value["export"] for t in filter(enabled_t, Target)]


# ----------------------------Color Filter ---------------------------------- #
class Filter(enum.Enum):
    BRIGHT     = 1
    DARK       = 2
    SATURATION = 3
