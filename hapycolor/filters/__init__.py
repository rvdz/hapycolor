"""
.. role:: python(code)
    :language: python

This module defines all the methods needed to interact with all the filters
implemented in the :mod:`hapycolor.filters` package.

To add a new filter, a class inheriting from :class:`base.Filter` needs to be
implemented and its module should be imported in this very module, else,
hapycolor will fail to find the new filter. Currently, the :func:`get` function
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

from . import lum_filter, reducer, base, kmeans_filter
from hapycolor import visual
from hapycolor import config


def get():
    #return [lum_filter.LumFilter, reducer.Reducer]
    return[kmeans_filter.KMeansFilter]


def apply(palette):
    """
    Apply all the enabled filters to a given palette
    """
    print("Filters found: " + ", ".join([f.__name__ for f in get()]))
    for filtr in get():
        palette = filtr.apply(palette)
        print("\nFiltered colors with " + filtr.__name__ + " ("
              + str(len(palette.visual_palette)) + "):")
        visual.print_palette(palette.visual_palette, size=1)
    return palette
