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

from . import vim, iterm, wallpaper, lightline, gnome, yabar
from . import base
from hapycolor import config
from hapycolor import exceptions


def initialize():
    """ Initialize config and/or choose to enable targets """
    print("Targets found: " + ", ".join([t.__name__ for t in get()]))
    targets = get_compatible()
    uninit_targets = []
    for t in targets:
        try:
            if not t.is_enabled():
                continue
            if not t.is_config_initialized():
                uninit_targets.append(t)
        except (KeyError, exceptions.InvalidConfigKeyError):
            uninit_targets.append(t)

    for t in uninit_targets:
        res = input("Enable " + t.__name__ + "? (y/n) :")
        if res.capitalize() == "Y":
            initialize_target(t)
        else:
            t.disable()


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


def is_target_subclass(target_str):
    try:
        clazz_str = "".join([t.title() for t in target_str.split("_")])
        clazz = eval(target_str + "." + clazz_str)
        if not issubclass(clazz, base.Target):
            return False
    except NameError:
        return False
    return True


def reconfigure(target_str):
    """
    Calls the :func:reconfigure method of the appropriate class
    contained in the target module provided in the arguments.
    This method allows to interact with the user and change the
    target settings.

    :param target_str: a string representing a target module.
    :raise: raises an :exc:`exceptions.InvalidTarget` if a module cannot be
        resolve from the provided string, or if there are no matching classes
        defined in the module that implement a :class:`Target`.
    """
    if not is_target_subclass(target_str):
        raise exceptions.InvalidTarget("Input does not match a module"
                                       + " containing a Target class")
    clazz_str = "".join([t.title() for t in target_str.split("_")])
    clazz = eval(target_str + "." + clazz_str)
    clazz.reconfigure()


def retry():
    """
    When initializing targets, asks for a retry if the user failed
    to enter correct inputs. This class is usefull in order to
    test the targets' initializations
    """
    res = input("\nAbort? (y/n): ").capitalize() == "Y"
    print("Abort: " + str(res))
    return res


def get_compatible():
    """
    Get all compatible targets
    """
    all_targets = base.Target.__subclasses__()
    # Filters out the incompatible or disabled targets
    return list(filter(lambda t: config.os() in t.compatible_os(),
                       all_targets))


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
