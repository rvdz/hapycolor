from . import base

import pathlib
from hapycolor import config
from hapycolor import exceptions
from hapycolor import helpers
from hapycolor import targets
from hapycolor.targets import yabar
from hapycolor.targets import wallpaper
import contextlib
from hapycolor import targets
import contextlib
import re


class I3(base.Target, config.ConfigurationEditor):
    """
    This class aims at altering i3's configuration file.
    Currently, it changes the color of the borders and sets the new
    wallpaper in addition of executing yabar with the custom configuration
    file
    """
    configuration_key = "config"

    border_variable = "$border_color"
    split_variable = "$split_color"

    def is_config_initialized():
        try:
            return I3.configuration_key in I3.load_config()
        except exceptions.InvalidConfigKeyError:
            return False

    def initialize_config():
        """
        Searches through the common path where is stored i3's configuration.
        If it isn't found, this function will prompt the user about its
        location, and save the result in hapycolor's configuration file.
        """
        config_path = None
        common_paths = [pathlib.Path(p).expanduser() for p in
                        ["~/.config/i3/config", "~/.i3/config"]]

        for p in common_paths:
            if p.is_file():
                config_path = p

        if config_path is None:
            p = helpers.input_path("Path to i3 configuration file: ")
            if not p.is_file():
                raise exceptions.WrongInputError("Must be a file")
            # Seems not useful
            # if not p.is_absolute():
            #     p = p.resolve()

        I3.save_config({I3.configuration_key: config_path.as_posix()})

    def compatible_os():
        return [targets.OS.LINUX]

    def export(palette, image_path):
        """
        .. todo::
            Change :func:`Target.is_enabled` so that it returns False
            when not present in the configuration file instead of letting
            an exception being raised.
        """
        border_color = palette.colors[0]
        split_color = palette.colors[1]

        I3.assign_border_colors()
        I3.declare_color(I3.border_variable, border_color)
        I3.declare_color(I3.split_variable, split_color)

        try:
            if targets.wallpaper.Wallpaper.is_enabled():
                I3.set_wallpaper(image_path)
        except exceptions.InvalidConfigKeyError:
            pass

        try:
            if targets.yabar.Yabar.is_enabled():
                I3.set_yabar()
        except exceptions.InvalidConfigKeyError:
            pass

    def declare_color(variable, color):
        """
        Associates a color to a variable
            set $variable_name <hex_color>
        """
        if not helpers.can_be_rgb(color):
            msg = "Color should be formatted as an RGB color. "
            msg += "Instead, {} was provided".format(color)
            raise exceptions.ColorFormatError(msg)

        hex_color = helpers.rgb_to_hex(color)

        config_file = I3.load_config()[I3.configuration_key]

        pattern_border = "set *{}.*".format(re.escape(variable))
        declaration = "set {}    {}".format(variable, hex_color)
        found = I3.replace_line(config_file, pattern_border,
                                lambda _: declaration)
        if not found:
            with open(config_file, 'r+') as f:
                f.write(declaration)

    def assign_border_colors():
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
        pattern = "^client\.focused (.*)$"
        base = "client.focused    {}    {}    {}    {}" \
            .format(I3.border_variable, I3.border_variable,
                    "{}", I3.split_variable)

        def new_line(match):
            text_color = [e for e in match.group(1).split(' ') if e != '']
            return base.format(text_color[2])

        config_file = I3.load_config()[I3.configuration_key]
        found = I3.replace_line(config_file, pattern, new_line)

        if not found:
            with open(config_file, 'r+') as f:
                f.write(base.format('#000000'))

    def set_wallpaper(image_path):
        pattern = r".*exec .*feh.*"
        config_file = I3.load_config()[I3.configuration_key]
        command = "exec --no-startup-id feh --bg-fill --no-xinerama {}" \
            .format(image_path)
        found = I3.replace_line(config_file, pattern, lambda _: command)

        if not found:
            with open(config_file, 'r+') as f:
                f.write(command)

    def set_yabar():
        pattern = r".*status_command *yabar.*"
        config_key = yabar.Yabar.configuration_key
        config_file = pathlib.Path(yabar.Yabar.load_config()[config_key]).parent / "hapy.conf"
        command = "status_command yabar -c {}".format(config_file.as_posix())

        found = I3.replace_line(config_file, pattern, lambda _: command)
        if not found:
            with open(config_file, 'r+') as f:
                f.write(command)
