from .export import iterm
from .export import vim

import configparser
import ctypes
import enum
import readline
import pathlib
import platform
import subprocess

########################## Initialize Config ###################################

project_config = "hapycolor/config.ini"

class OS(enum.Flag):
    LINUX  = 0
    DARWIN = 1

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
        raise NotImplementedError

    p = p / "hapycolor" / "colors"
    if not p.exists():
        p.mkdir(parents=True)
    save_config("export", "colorscheme_vim", (p / "hapycolor.vim").as_posix())


def save_iterm():
    """ Checks if the iTerm preferences file is correct and save it in the
        project configuration file """
    p = input_path("Path to iTerm config file: ")
    if not p.is_absolute():
        p = p.resolve()
    if p.name != "com.googlecode.iterm2.plist":
        raise NotImplementedError
    if not p.is_file():
        raise NotImplementedError
    save_config("export", "iterm_config", p.as_posix())

def save_config(section, key, value):
    """ Save a new entry in the config file """
    config = configparser.ConfigParser()
    config.read(project_config)
    config[section][key] = value
    with open(project_config, "w") as f:
        config.write(f)

class Feature(enum.Enum):
    """ Links each feature with its:
            - name
            - system compatibility
            - configuration save function
            - export function
            - boolean indicating if the feature has been enabled
            - configuration value's key
                                    """

    VIM            = {"name"     : "Vim",
                      "os"       : OS.LINUX | OS.DARWIN,
                      "save"     : save_vim,
                      "export"   : iterm.Iterm.profile,
                      "support"  : "vim_support",
                      "key"      : "colorscheme_vim"}

    ITERM          = {"name"     : "iTerm",
                      "os"       : OS.DARWIN,
                      "save"     : save_iterm,
                      "export"   : vim.Vim.profile,
                      "support"  : "iterm_support",
                      "key"      : "iterm_config"}

    GNOME_TERMINAL = {"name"     : "gnome-terminal",
                      "os"       : OS.LINUX,
                      "save"     : NotImplemented,
                      "export"   : NotImplemented,
                      "support"  : "gnome_terminal_support",
                      "key"      : "gnome"}

def init_configs():
    """ Intializes the features that are compatible and not disabled """
    config = load_config("export")

    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(readline.get_completer())

    # Filters undefined compatible and not disabled features
    f = lambda x: x.value["os"] == os() \
            and (x.value["support"] not in config or config[x.value["support"]] != "False") \
            and x.value["key"] not in config

    for e in filter(f, Feature):
        res = input("Enable " + e.value["name"] + "? (y/n) :")
        is_enabled = False
        if res.capitalize() == "Y":
            e.value["save"]()
            is_enabled = True
        save_config("export", e.value["support"], str(is_enabled))


############################# Access Config ####################################
def app_name():
    return load_config("core")["app_name"]

def vim():
    return load_config("export")["colorscheme_vim"]

def load_config(section):
    config = configparser.ConfigParser()
    config.read(project_config)
    return config[section]

def get_keys():
    return load_config("hyerplan")["keys"]

def os():
    if platform.system() == "Darwin":
        return OS.DARWIN
    else:
        return OS.LINUX

def iterm_template():
    return load_config("export")["iterm_template"]

def iterm_config():
    return load_config("export")["iterm_config"]

def hyperplan_file(filter_type):
    config = load_config("hyperplan")
    if filter_type == Filter.DARK:
        return config["dark"]
    elif filter_type == Filter.BRIGHT:
        return config["bright"]
    elif filter_type == Filter.SATURATION:
        return config["saturation"]
    else:
        raise AttributeError("Unknown filter type")

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
               ["-o"], [config["library"] + library_type], [config["source"]]]
    if not pathlib.Path(config["library"] + library_type).is_file():
        p = subprocess.Popen([item for sublist in command for item in sublist])
        p.wait()
    return ctypes.cdll.LoadLibrary(config["library"] + library_type)

def export_functions():
    """ Retrives the export functions for the enabled features """
    config = load_config("export")
    f = lambda x: x.value["os"] == os() and config[x.value["support"]] == "True"
    return map(lambda x : x.value["export"], filter(f, Feature))

############################# Color Filter #####################################
class Filter(enum.Enum):
    BRIGHT     = 1
    DARK       = 2
    SATURATION = 3
