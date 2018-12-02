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
from . import vim, iterm, wallpaper, lightline, gnome_terminal, yabar, i3, rofi
from . import base


def initialize():
    """ Initialize config and/or choose to enable targets """
    print("Targets found: " + ", ".join([t.__name__ for t in get()]))
    targets = get_compatible()
    uninit_targets = []

    for target in targets:
        if not target.is_defined() \
                or (target.is_enabled() and not target.is_config_initialized()):
            uninit_targets.append(target)

    for target in uninit_targets:
        res = input("Enable " + target.__name__ + "? (y/n) :")
        if res.capitalize() == "Y":
            initialize_target(target)
        else:
            target.disable()


def initialize_target(target):
    """
    Initializes a given target. If the intialization is successful, i.e. the
    user entered a correct information, then, the target's section 'enabled' of
    the configuration file will be saved as 'True', in addition of saving other
    possible data. Else, the former section will be marked as 'False'.

    :arg target: one of the subclasses of :class:`Target`
    """
    while 1:
        try:
            target.initialize_config()
        except exceptions.WrongInputError as e:
            print(e.msg)
        else:
            target.enable()
            break
        if not retry():
            target.disable()
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
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    msg = "Input does not match a module containing a Target class"
    try:
        clazz = eval(convert(target_str) + "." + target_str)
    except AttributeError:
        raise exceptions.InvalidTarget(msg)

    if not is_target_subclass(clazz):
        raise exceptions.InvalidTarget(msg)
    return clazz


def reconfigure(target_str):
    """
    Calls the :func:reconfigure method of the appropriate class
    contained in the target module provided in the arguments.
    This method allows to interact with the user and change the
    target settings.

    :param target_str: a string representing a target module.
    """
    clazz = get_class(target_str)
    clazz.reconfigure()


def enable(target_str):
    """
    Calls the :func:targets.base.Target.enable() method of the appropriate class
    contained in the target module provided in the arguments.
    """
    clazz = get_class(target_str)
    if clazz.is_enabled():
        return 1
    clazz.enable()
    return 0


def disable(target_str):
    """
    Calls the :func:targets.base.Target.disable() method of the appropriate class
    contained in the target module provided in the arguments.
    """
    clazz = get_class(target_str)
    if not clazz.is_enabled():
        return 1
    clazz.disable()
    return 0


def retry():
    """
    When initializing targets, asks for a retry if the user failed
    to enter correct inputs. This class is usefull in order to
    test the targets' initializations
    """
    res = input("\nAbort? (y/n): ").capitalize() == "Y"
    print("Abort: " + str(res))
    return res


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
