from enum import auto, Enum

class FilterEnum(Enum):
    BRIGHT     = auto()
    DARK       = auto()
    SATURATION = auto()

class Config:
    APP_NAME  = "hapycolor"
    keys_file = "keys.json"

    def get_hyperplan_file(filter_type):
        if filter_type == FilterEnum.DARK:
            return "../hyperplan_robin/dark.json"
        elif filter_type == FilterEnum.BRIGHT:
            return "../hyperplan_robin/light.json"
        elif filter_type == FilterEnum.SATURATION:
            return "../hyperplan_yann/saturations.json"
        else:
            raise AttributeError("Unknown filter type")