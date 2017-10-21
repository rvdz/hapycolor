import os
import sys
from enum import Enum

dirname = os.path.dirname(os.path.realpath(sys.argv[0]))

class FilterEnum(Enum):
    BRIGHT     = 1
    DARK       = 2
    SATURATION = 3

class Config:
    APP_NAME  = "hapycolor"
    keys_file = "keys.json"
    ITERM_CONFIG = "/Users/yanncolina/Documents/com.googlecode.iterm2.plist"
    ITERM_TEMPLATE = "template.xml"
    COLORSCHEME_VIM = "/Users/yanncolina/.vim_runtime/sources_non_forked/hapycolor/colors/hapycolor.vim"

    def get_hyperplan_file(filter_type):
        if filter_type == FilterEnum.DARK:
            return dirname + "/../hyperplan_robin/dark.json"
        elif filter_type == FilterEnum.BRIGHT:
            return dirname + "/../hyperplan_robin/light.json"
        elif filter_type == FilterEnum.SATURATION:
            return dirname + "/../hyperplan_yann/saturations.json"
        else:
            raise AttributeError("Unknown filter type")
