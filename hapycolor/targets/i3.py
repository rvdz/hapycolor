"""
i3 Module
"""
import pathlib
import re
from hapycolor import exceptions
from hapycolor import helpers
from hapycolor import targets
from hapycolor.targets import wallpaper
from . import base


class I3(base.Target):
    """
    This class aims at altering i3's configuration file.
    Currently, it changes the color of the borders and sets the new
    wallpaper in addition of executing yabar with the custom configuration
    file
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

        This class defines three main features related to i3
        - border color definition
        - sets the new wallpaper
        - calls yabar with the new configuration file

        .. todo::
            Add rofi support
        """
        border_color = palette.colors[0]
        split_color = palette.colors[1]

        config_path = I3.load_config()[I3.configuration_key]
        configuration = []
        with open(config_path, 'r') as config_file:
            configuration = config_file.read().splitlines()

        configuration = I3.assign_border_colors(configuration)
        configuration = I3.declare_color(configuration, I3.border_variable,
                                         border_color)
        configuration = I3.declare_color(configuration, I3.split_variable,
                                         split_color)

        # TODO(yann) is_enabled() should return False if not initialized,
        # when this will be changed, remove the try/catch
        try:
            if wallpaper.Wallpaper.is_enabled():
                configuration = I3.set_wallpaper(configuration, image_path)
        except exceptions.InvalidConfigKeyError:
            pass

        with open(config_path, 'w') as config_file:
            config_file.write('\n'.join(configuration))

    @staticmethod
    def declare_color(config, variable, color):
        """
        Associates a color to a variable
            set $variable_name <hex_color>
        """
        if not helpers.can_be_rgb(color):
            msg = "Color should be formatted as an RGB color. "
            msg += "Instead, {} was provided".format(color)
            raise exceptions.ColorFormatError(msg)

        hex_color = helpers.rgb_to_hex(color)

        pattern = r"set +{}".format(re.escape(variable))
        replace = "set {}    {}".format(variable, hex_color)

        return I3.replace_or_add(config, pattern, replace)

    @staticmethod
    def assign_border_colors(config):
        """
        Assings the variables associated to the colors of the border to i3's
        variable: `client.focused`, which takes four colors:
            - border color
            - background color
            - text color
            - split color

        The first two colors will be matched with the `$focused_border_color`,
        whereas the split color will be associated to `$focused_split_color`.

        .. note::
            If `client.focused` wasn't already defined the text color will be
            set to black (#000000), otherwise, the former color will be used.
        """
        pattern = r"client.focused +(\S+) +(\S+) +(\S+) +(\S+)"
        replace = "client.focused    {}    {}    {}    {}" \
            .format(I3.border_variable, I3.border_variable,
                    "{}", I3.split_variable)
        match = False
        new_config = []
        for line in config:
            if re.match(pattern, line):
                match = re.match(pattern, line)
                new_config.append(replace.format(match.group(3)))
                match = True
            else:
                new_config.append(line)

        if not match:
            new_config = [replace.format("#000000")] + config
        return new_config

    @staticmethod
    def set_wallpaper(config, image_path):
        """
        If the target "wallpaper" is set, this method will insert/replace feh's
        command in order to update the current wallpaper.
        """
        pattern = r".*exec .+feh"
        command = "exec --no-startup-id feh --bg-fill --no-xinerama {}" \
            .format(image_path)
        return I3.replace_or_add(config, pattern, command)

    @staticmethod
    def replace_or_add(config, pattern, replace):
        """
        Handy method that loops through a list of strings and if a line
        matches the provided pattern, it will replace it with the provided
        string. If no match is found, the `replace` argument will be added
        at the begining of the list.

        :arg config: The current configuration file loaded as a list of
            strings.
        :arg pattern: A raw string defining a regular expression.
        :arg replace: The new string which will be used to replace the matched
            string.

        :see: `https://stackoverflow.com/questions/2081640/what-exactly-do-u-\
                and-r-string-flags-do-and-what-are-raw-string-literals`
        """
        new_config = []
        match = False
        for line in config:
            if re.match(pattern, line):
                new_config.append(replace)
                match = True
            else:
                new_config.append(line)

        if not match:
            new_config = [replace] + config
        return new_config
