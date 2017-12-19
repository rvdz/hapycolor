"""
.. role:: python(code)
    :language: python

This module defines all the methods needed to interact with all the filters
implemented in the :mod:`hapycolor.filters` package.

To add a new filter, a class inheriting from :class:`base.Filter` needs to be
implemented and its module should be imported in this very module, else,
hapycolor will fail to find the new filter. Currently, the :func:`get_filter` function
needs the class to be named after a PascalCase version of its module's name.

.. note::
    A list `__all__` could be used to define all the modules to be imported and
    then :python:`from . import *` would import them all, but strangely,
    in this case, sphinx_ fails to generate the documentation of this file.

.. _sphinx: http://www.sphinx-doc.org/en/stable/

.. note:: Maybe, a future version of this project would be able to get rid of
    the class name/module name constraint by analyzing the classes contained
    in the module and retrieving the one that implements :class:`base.Filter`.
"""

from . import luminosity_filter, reducer
from . import base
from hapycolor import visual
from hapycolor import config

def get_filters():
    """
    Returns all the filters enabled sorted by their complexity.
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
