__all__ = [
           "vim",
           "iterm",
           "wallpaper",
           "base",
          ]

from . import *
from hapycolor import config
from hapycolor import exceptions

def initialize():
    """ Initialize config and/or choose to enable targets """
    print("Targets found: ", [t.__name__ for t in get()])
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


def retry():
    """
    When initializing targets, asks for a retry if the user failed
    to enter correct inputs. This class is usefull in order to
    test the targets' initializations
    """
    return input("\nAbort? (y/n): ").capitalize() == "Y"


def get_compatible():
    """
    Get all compatible targets
    """
    all_targets = base.Target.__subclasses__()
    # Filters out the incompatible or disabled targets
    return list(filter(lambda t: config.os() in t.compatible_os(), all_targets))

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
