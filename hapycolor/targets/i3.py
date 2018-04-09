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

    border_variable = "$border_color"
    split_variable = "$split_color"
    configuration_key = "config"

    def get_config_file():
        """
        ConfigurationEditor requires to specify the location of the
        configuration file. Since all the classes are static, the configuration
        file cannot directly be stored as an argument of the class, since its
        super function method :func:`Target.load_config()` cannot be called in
        the body of :class:`I3` outside a function.
        """
        return I3.load_config()[I3.configuration_key]

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
        common_paths = [pathlib.Path(p) for p in
                        ["~/.config/i3/config", "~/.i3/config"]]

        for p in common_paths:
            if p.is_file():
                config_path = p

        if not config_path:
            p = helpers.input_path("Path to i3 configuration file: ")
            if not p.is_file():
                raise exceptions.WrongInputError("Must be a file")
            # Seems not useful
            # if not p.is_absolute():
            #     p = p.resolve()

        I3.save_config({I3.configuration_key: p.as_posix()})

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
        I3.declare_border_colors(border_color, split_color)
        I3.assign_border_colors()

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

    def declare_border_colors(border_color, split_color):
        """
        Associates the color variables to the colors themselves.
        The result of this function should be:

            set $focused_border_color = <hex_color>
            set $focused_split_color = <hex_color>
        """
        for c in [border_color, split_color]:
            if not helpers.can_be_rgb(c):
                msg = "Color should be formatted as an RGB color. "
                msg += "Instead, {} was provided".format(c)
                raise exceptions.ColorFormatError(msg)

        bc = helpers.rgb_to_hex(border_color)
        sc = helpers.rgb_to_hex(split_color)

        I3.replace_line(".*{}.*".format(I3.border_variable),
                        lambda m: "set {} {}\n".format(I3.border_variable, bc))

        I3.replace_line(".*{}.*".format(I3.split_variable),
                        lambda m: "set {} {}\n".format(I3.split_variable, sc))

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
        pattern = "^client.focused\t.*\t.*\t(.*)\t.*"
        base = "client.focused\t{}\t{}\t{}\t{}" \
            .format(I3.border_variable, I3.border_variable,
                    "{}", I3.split_variable)

        def new_line(match=None):
            c = match.group(1) if match else "#000000"
            return base.format(c) + '\n'

        I3.replace_line(pattern, new_line)

    def set_wallpaper(image_path):
        pattern = r".*exec .*feh.*"
        command = "exec --no-startup-id feh --bg-fill --no-xinerama {}" \
            .format(image_path)
        I3.replace_line(pattern, lambda m: command)

    def set_yabar():
        pattern = r".*yabar.*"
        config_key = yabar.Yabar.configuration_key
        command = "yabar -c {}".format(yabar.Yabar.load_config()[config_key])
        I3.replace_line(pattern, lambda m: command)
