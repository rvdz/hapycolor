import abc
from hapycolor import config
from hapycolor import exceptions

class Target(metaclass=abc.ABCMeta):
    """
    Abstract class introducting the basic methods needed to initialize the target
    and export the palette or the image to the environment. The subclasses need
    to implement:

    - How to initialize the target
    - Function that states if the target has already be correctly initialized
    - A function that retrives a list of the compatible operating systems
    - The export function which will be called by passing the palette and the path of the image

    Each target has a dedicated section in the configuration file from which
    it can load or save its own data. To do so, the class provides five class
    methods that aim at:

    - Loading the section of the configuration file
    - Adding or modifying information stored in the configuration file
    - Enabling the target
    - Disabling the target
    - Check if the target is enabled

    """
    # Static Methods
    @staticmethod
    def initialize_config():
        pass

    @staticmethod
    def is_config_initialized():
        return True

    # Abstract Static Methods
    @abc.abstractstaticmethod
    def export(palette, image_path):
        raise exceptions.CallingAbstractMethodError("Your are a wizard!")

    @abc.abstractstaticmethod
    def compatible_os():
        """ Returns a list of enum of class :class:`hapycolor.config.OS` """
        raise exceptions.CallingAbstractMethodError("Your are a wizard!")

    # Class Methods
    @classmethod
    def load_config(cls):
        """
        Loads the configuration related to the subclass and returns a dictionary.
        """
        return config.load(cls.__name__)

    @classmethod
    def save_config(cls, target_config):
        return config.save(cls.__name__, target_config)

    @classmethod
    def enable(cls):
        config.save(cls.__name__, {"enabled" : True})

    @classmethod
    def disable(cls):
        config.save(cls.__name__, {"enabled" : False})

    @classmethod
    def is_enabled(cls):
        return cls.load_config()["enabled"] == str(True)
