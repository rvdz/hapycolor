"""
Rofi module
"""
import pathlib
from hapycolor import helpers
from hapycolor import targets
from hapycolor import exceptions
from hapycolor.targets import base
from hapycolor.configuration_editor import ConfigurationEditor

class Rofi(base.Target):
    """
    ROFI
    """
    template_key = "template"
    configuration_key = "config"


    @staticmethod
    def get_config_file():
        return Rofi.load_config()[Rofi.configuration_key]


    @staticmethod
    def is_config_initialized():
        try:
            return Rofi.configuration_key in Rofi.load_config()
        except exceptions.InvalidConfigKeyError:
            return False


    @staticmethod
    def initialize_config():
        """
        Searches through the common paths where is stored Rofi's configuration.
        If it isn't found, this function will prompt the user about its
        location, and save the result in hapycolor's configuration file.

        Then, prompts the user about a configuration file to be used as a
        template. Its format is described here.

        .. todo::
            Create a section in the documentation detailing how to create a
            rofi or yabar template file.
        """
        config_path = None
        common_paths = [pathlib.Path(p) for p in ["~/.config/rofi"]]

        for path in common_paths:
            if path.is_dir():
                config_path = path

        if not config_path:
            config_path = helpers.input_path("Path to rofi configuration directory: ")
            if not config_path.is_dir():
                raise exceptions.WrongInputError("Must be a directory")
            # Seems not needed
            # if not p.is_absolute():
            #     p = p.resolve()

        Rofi.save_config({Rofi.configuration_key: config_path.as_posix()})

        config_path = helpers.input_path("Path to rofi template (for more "
                                         + "information about template files, "
                                         + "please check out here: ")

        if not config_path.exists():
            raise exceptions.WrongInputError("{} not found"
                                             .format(config_path.as_posix()))
        if not config_path.is_file():
            raise exceptions.WrongInputError("{} is not a file"
                                             .format(config_path.as_posix()))

        Rofi.save_config({Rofi.template_key: config_path.as_posix()})


    @staticmethod
    def compatible_os():
        return [targets.OS.LINUX]

    @staticmethod
    def export(palette, image_path):
        with open(Rofi.load_config()[Rofi.template_key], 'r') as template_file:
            template = template_file.read().splitlines()
        editor = ConfigurationEditor(template)
        filled_template = editor.replace(palette)

        config_path = Rofi.load_config()[Rofi.configuration_key]
        with open(config_path, 'w') as config_file:
            config_file.write(filled_template)
