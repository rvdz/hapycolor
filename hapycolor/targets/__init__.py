"""
.. role:: python(code)
    :language: python

This module defines all the methods needed to interact with all the targets
implemented in the :mod:`hapycolor.targets` package.

To add a new target, a class inheriting from :class:`base.Target` needs to be
implemented and its module should be imported in this very module, else,
hapycolor will fail to find the new target. Currently, the :func:`reconfigure`
function needs the class to be named after a PascalCase version of its module's
name.

.. note::
    A list `__all__` could be used to define all the modules to be imported and
    then :python:`from . import *` would import them all, but strangely,
    in this case, sphinx_ fails to generate the documentation of this file.

.. _sphinx: http://www.sphinx-doc.org/en/stable/

.. note:: Maybe, a future version of this project would be able to get rid of
    the class name/module name constraint by analyzing the classes contained
    in the module and retrieving the one that implements :class:`base.Target`.
"""

import platform
import enum
import re
from hapycolor import config
from hapycolor import exceptions
from hapycolor.targets import vim, iterm, wallpaper, lightline, gnome_terminal, \
                              yabar, i3, rofi, base


def initialize_target(target):
    """
    Initializes a given target. If the intialization is successful, i.e. the
    user entered a correct information, then, the target's section 'enabled' of
    the configuration file will be saved as 'True', in addition of saving other
    possible data. Else, the former section will be marked as 'False'.

    :arg target: one of the subclasses of :class:`Target`
    """
    print("Initializing {}".format(target.__name__))
    while not target.is_config_initialized():
        try:
            target.initialize_config()
        except exceptions.WrongInputError as e:
            print(e.msg)
            if not retry():
                break

def reconfigure(target):
    while 1:
        try:
            target.reconfigure()
            break
        except exceptions.WrongInputError as e:
            print(e.msg)
        if not retry():
            break


def is_target_subclass(clazz):
    try:
        return issubclass(clazz, base.Target)
    except TypeError:
        return False


def get_class(target_str):
    """
    Returns the class which name correspond to the string

    :param target_str: a string representing a target module.
    :raise: raises an :exc:`exceptions.InvalidTarget` if a module cannot be
        resolve from the provided string, or if there are no matching classes
        defined in the module that implement a :class:`Target`.
    """
    def convert(name):
        """Convert PascalCase to snake_case"""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    msg = "Input {} does not match a module containing a Target class".format(target_str)
    try:
        clazz = eval(convert(target_str) + "." + target_str)
    except (AttributeError, NameError) as err:
        raise exceptions.InvalidTarget(msg) from err

    if not is_target_subclass(clazz):
        raise exceptions.InvalidTarget(msg)
    return clazz


def retry():
    """
    When initializing targets, asks for a retry if the user failed
    to enter correct inputs. This class is usefull in order to
    test the targets' initializations
    """
    return input("\nAbort? (y/n): ").lower() == "n"


def get_all_names():
    """
    Get all target names
    """
    all_targets = base.Target.__subclasses__()
    return [t.__name__ for t in all_targets]


class OS(enum.Enum):
    LINUX = 0
    DARWIN = 1


def os():
    platform_os = platform.system()
    if platform_os == "Darwin":
        return OS.DARWIN
    elif platform_os == "Linux":
        return OS.LINUX
    else:
        raise exceptions.PlatformNotSupportedError()


def get_compatible():
    """
    Get all compatible targets
    """
    all_targets = base.Target.__subclasses__()
    # Filters out the incompatible or disabled targets
    return list(filter(lambda t: os() in t.compatible_os(),
                       all_targets))


def get_compatible_names():
    """
    Get str names of all compatible targets
    """
    return [t.__name__ for t in get_compatible()]


def get_enabled():
    """
    Get all enabled targets
    """
    all_targets = base.Target.__subclasses__()
    return list(filter(lambda t: t.is_enabled() == True, all_targets))


def get():
    return base.Target.__subclasses__()


def export(palette, image_path):
    """
    Exports a palette to all the compatible and enabled targets
    """
    targets = get_compatible()
    for t in targets:
        if t.is_enabled():
            print("Exporting: ", t.__name__)
            try:
                t.export(palette, image_path)
            except exceptions.ExportTargetFailure as e:
                print(str(e))
                e.disable_target()
