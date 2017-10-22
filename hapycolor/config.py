from enum import auto, Enum
import configparser
import platform
import subprocess
import pathlib
from ctypes import cdll

class Filter(Enum):
    BRIGHT     = auto()
    DARK       = auto()
    SATURATION = auto()

class OS(Enum):
    LINUX  = 0
    DARWIN = 1

def app_name():
    return load_config("core")["app_name"]

def vim():
    return load_config("export")["colorscheme_vim"]

def load_config(section):
    config = configparser.ConfigParser()
    config.read("config.ini")
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

def iterm_config()
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

def get_library():
    config = load_config("reducer")
    system_options = ""
    library_type = ""
    if os() == OS.DARWIN:
        system_options = "-dynamiclib -o"
        library_type = ".dylib"
    else:
        system_options = "-fPIC -shared -o"
        library_type = ".so"

    command = [config["compiler"], config["options"], system_options, config["library"] \
               + library_type, config["source"]]
    if not pathlib.Path(config["library"] + library_type).is_file():
        print(command)
        subprocess.call(command)
    return cdll.LoadLibrary("./" + config["library"] + library_type)
