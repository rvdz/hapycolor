__all__ = [
           "luminosity_filter",
           "reducer",
          ]

from . import *
from . import base
from hapycolor import visual
from hapycolor import config

def get_filters():
    """
    Returns all the filters enabled. TODO: Currently, this is done manually,
    but in a future version, this could be integrated with the configuration
    file.
    """
    fltrs_config = config.load("Filters")
    fltrs = [f for f in config.load("Filters")]
    # Sort the filters according to their complexity
    fltrs.sort(key=lambda f: int(fltrs_config[f]))

    fltr_classes = []
    for f in fltrs:
        # Convert to PascalCase
        clazz = "".join(x.title() for x in f.split('_'))
        fltr_classes.append(eval(f + "." + clazz))
    return fltr_classes


def apply(palette):
    """
    Apply all the enabled filters to a given palette
    """
    print("Filters found: " + str([f.__name__ for f in get_filters()]))
    for filtr in get_filters():
        palette = filtr.apply(palette)
        print("\nFiltered colors with " + filtr.__name__ + " (" + str(len(palette.colors)) + "):")
        visual.print_palette(palette.colors, size=1)
    return palette
