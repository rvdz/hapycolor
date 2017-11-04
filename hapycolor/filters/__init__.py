__all__ = [
           "luminosity_filter",
           "reducer",
           "base",
          ]

from . import *
from hapycolor import visual

def get_filters():
    """
    Returns all the filters enabled. TODO: Currently, this is done manually,
    but in a future version, this could be integrated with the configuration
    file.
    """
    return [luminosity_filter.LuminosityFilter, reducer.Reducer]

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
