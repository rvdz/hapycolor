"""
i3 Module
"""
import pathlib
import re
from hapycolor import exceptions
from hapycolor import helpers
from hapycolor import targets
from hapycolor.configuration_editor import ConfigurationEditor
from hapycolor.targets import wallpaper
from . import base


class I3(base.Target):
    """
    This class aims at altering i3's configuration file.
    Currently, it changes the color of the borders and sets the new
    wallpaper in addition of executing yabar with the custom configuration
    file.
    """
    configuration_key = "config"

    border_variable = "$border_color"
    split_variable = "$split_color"

    @staticmethod
    def is_config_initialized():
        try:
            return I3.configuration_key in I3.load_config()
        except exceptions.InvalidConfigKeyError:
            return False

    @staticmethod
    def initialize_config():
        """
        Searches through the common path where is stored i3's configuration.
        If it isn't found, this function will prompt the user about its
        location, and save the result in hapycolor's configuration file.
        """
        config_path = None
        common_paths = [pathlib.Path(p).expanduser() for p in
                        ["~/.config/i3/config", "~/.i3/config"]]

        for path in common_paths:
            if path.is_file():
                config_path = path

        if config_path is None:
            path = helpers.input_path("Path to i3 configuration file: ")
            if not path.is_file():
                raise exceptions.WrongInputError("Must be a file")
            # Seems not useful
            # if not p.is_absolute():
            #     p = p.resolve()

        I3.save_config({I3.configuration_key: config_path.as_posix()})

    @staticmethod
    def compatible_os():
        return [targets.OS.LINUX]

    @staticmethod
    def export(palette, image_path):
        """
        .. todo::
            Change :func:`Target.is_enabled` so that it returns False
            when not present in the configuration file instead of letting
            an exception being raised.

        This class implements two main features:
        - it replaces the wallpaper in the configuration file
        - replaces the colors preceded by the macro replace line, for more info,
            please check out :class:`hapycolor.configuration_editor.ConfigurationEditor`:
        """
        config_path = I3.load_config()[I3.configuration_key]
        configuration = []
        with open(config_path, 'r') as config_file:
            configuration = config_file.read().splitlines()

        # TODO(yann) is_enabled() should return False if not initialized,
        # when this will be changed, remove the try/catch
        try:
            if wallpaper.Wallpaper.is_enabled():
                configuration = I3.set_wallpaper(configuration, image_path)
        except exceptions.InvalidConfigKeyError:
            pass

        configuration = ConfigurationEditor(configuration).replace(palette)

        with open(config_path, 'w') as config_file:
            config_file.write('\n'.join(configuration))

    @staticmethod
    def set_wallpaper(config, image_path):
        """
        If the target "wallpaper" is set, this method will insert/replace feh's
        command in order to update the current wallpaper.
        """
        pattern = r".*exec .+feh"
        command = "exec --no-startup-id feh --bg-fill {}".format(image_path)

        new_config = []
        match = False
        for line in config:
            if re.match(pattern, line):
                new_config.append(command)
                match = True
            else:
                new_config.append(line)

        if not match:
            new_config = [replace] + config
        return new_config
