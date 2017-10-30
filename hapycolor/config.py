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

########################## Initialize Config ###################################

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


def input_path(prompt):
    """ Prompts the user and retrives a 'Path' object """
    return pathlib.Path(input(prompt)).expanduser()

def save_vim():
    """ Creates the path where the colorscheme will be generated, and stores it
        in the project configuration file """
    p = input_path("Path to vim's custom plugins directory: ")
    if not p.is_absolute():
        p = p.resolve()

    if not p.is_dir():
        raise exceptions.WrongInputError("Must be a directory")

    p = p / "hapycolor" / "colors"
    if not p.exists():
        p.mkdir(parents=True)
    save_config("export", Target.VIM.value["key"], (p / "hapycolor.vim").as_posix())


def save_iterm():
    """ Checks if the iTerm preferences file is correct and save it in the
        project configuration file """
    p = input_path("Path to iTerm configuration file: ")
    if not p.is_absolute():
        p = p.resolve()
    if not p.is_file():
        raise exceptions.WrongInputError("Entered path does not lead to a file")
    if p.name != "com.googlecode.iterm2.plist":
        raise exceptions.WrongInputError("The file does not match an iTerm configuration file")
    save_config("export", Target.ITERM.value["key"], p.as_posix())

def save_config(section, key, value):
    """ Save a new entry in the config file """
    config = configparser.ConfigParser()
    config.read(get_config())
    config[section][key] = value
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
    """ Intializes the target that are compatible and not disabled """
    config = load_config("export")

    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(readline.get_completer())

    # Filters undefined compatible and not disabled target
    f = lambda x: os() in x.value["os"] \
            and (x.value["enabled"] not in config)

    for t in filter(f, Target):
        res = input("Enable " + t.value["name"] + "? (y/n) :")
        initialize_target(t, res.capitalize() == "Y")

def initialize_target(target, is_enabled):
    correct_entry = False
    while target.value["save"] and is_enabled and not correct_entry:
        try:
            target.value["save"]()
        except exceptions.WrongInputError as e:
            print(e.mssg)
        else:
            break
        if input("\nAbort? (y/n): ").capitalize() == "Y":
            is_enabled = False
            correct_entry = True
    save_config("export", target.value["enabled"], str(is_enabled))


############################# Access Config ####################################
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

def get_reduce_library():
    """ Compiles if necessary and load the reducer library """
    config = load_config("reducer")
    system_options = []
    library_type = ""
    if os() == OS.DARWIN:
        system_options = ["-dynamiclib"]
        library_type = ".dylib"
    else:
        system_options = ["-fPIC", "-shared"]
        library_type = ".so"

    command = [[config["compiler"]], config["options"].split(), system_options, \
               ["-o"], [ROOT_DIR + "/" + config["library"] + library_type], [ROOT_DIR + "/" + config["source"]]]
    if not pathlib.Path(ROOT_DIR + "/" + config["library"] + library_type).is_file():
        p = subprocess.Popen([item for sublist in command for item in sublist])
        p.wait()
    return ctypes.cdll.LoadLibrary(ROOT_DIR + "/" + config["library"] + library_type)

def get_export_functions():
    """ Retrives the export functions for the enabled target """
    target_config = load_config("export")
    f = lambda x: (os() in x.value["os"]) and (target_config[x.value["enabled"]] == "True")
    return map(lambda x : x.value["export"], filter(f, Target))

############################# Color Filter #####################################
class Filter(enum.Enum):
    BRIGHT     = 1
    DARK       = 2
    SATURATION = 3
