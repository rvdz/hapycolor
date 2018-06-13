import os
import subprocess as sp

from hapycolor import exceptions
from hapycolor import helpers
from hapycolor import palette as pltte
from hapycolor import targets
from hapycolor.helpers import rgb_to_hex
from . import base
from . import pam
from . import terminal_color_manager as tcm


class GnomeTerminal(base.Target):

    """
        Creates a Gnome-Terminal theme

        Erases the default one if it has not been changed
        Otherwise appends a new one to the list
    """

    configuration_key = "gnome_terminal_profiles"
    default_key = "default"

    @staticmethod
    def initialize_config():
        """
            Set the path for themes
        """
        default_path = '/org/gnome/terminal/legacy/profiles:'
        p = helpers.input_path("Path to gnome-terminal's dconf profiles\n\
                               (Keep empty to use default path '{}'): "
                               .format(default_path))
        if str(p) == '.':
            new_config = {GnomeTerminal.configuration_key: default_path}
            GnomeTerminal.save_config(new_config)
        elif str(p)[-1] != ':':
            raise exceptions.WrongInputError("Must end with ':'")

        is_default = GnomeTerminal.set_default()

        GnomeTerminal.save_config({GnomeTerminal.default_key: str(is_default)})

    def set_default():
        answ = input("Set generated profile as default? (y/n): ").upper()
        if answ == "Y":
            return True
        elif answ == "N":
            return False
        else:
            print("Wrong input")
            return GnomeTerminal.set_default()

    @staticmethod
    def is_config_initialized():
        try:
            config = GnomeTerminal.load_config()
            is_init = GnomeTerminal.configuration_key in config \
                    and GnomeTerminal.default_key in config
        except exceptions.InvalidConfigKeyError:
            return False
        return is_init

    @staticmethod
    def compatible_os():
        return [targets.OS.LINUX]

    @staticmethod
    def export(palette, image_path):
        """
            Creates a Gnome Terminal profile
            Requires a 18 colors palette in rgb format
        """

        if palette.__class__ != pltte.Palette:
            msg = "The palette does not respect the appropriate structure"
            raise exceptions.PaletteFormatError(msg)

        is_default = GnomeTerminal.load_config()[GnomeTerminal.default_key]
        is_default = is_default == str(True)

        if is_default:
            old_profiles = GnomeTerminal.get_profiles()

        name = os.path.splitext(os.path.basename(image_path))[0]
        GnomeTerminal.create_profile(palette, name)

        if is_default:
            new_profiles = GnomeTerminal.get_profiles()
            new_profile = (new_profiles - old_profiles).pop()
            GnomeTerminal.set_as_default(new_profile)

    @staticmethod
    def create_profile(palette, name):
        """
        From a palette and the image's name, generates a gnome-terminal
        profile.
        """
        if not palette.colors:
            msg = 'The palette does not contain any color'
            raise exceptions.PaletteFormatError(msg)

        config = GnomeTerminal.load_config()
        saved_profiles_path = config[GnomeTerminal.configuration_key]
        fg = rgb_to_hex(palette.foreground)
        bg = rgb_to_hex(palette.background)

        colors = tcm.TerminalColorManager(palette.colors)()

        hex_colors = list(map(rgb_to_hex, colors))
        hex_colors = '", "'.join(hex_colors)
        hex_colors = '"' + hex_colors + '"'
        process = sp.Popen(['bash', './hapycolor/targets/export_gnome.sh',
                            name, fg, bg, hex_colors,
                            saved_profiles_path], stdout=sp.PIPE, bufsize=1)
        with process.stdout:
            for line in iter(process.stdout.readline, b''):
                print(line, )
        process.wait()

    @staticmethod
    def get_profiles():
        """
        Returns a set containing the name of the current gnome-terminal
        profiles.
        """
        get_profiles_command = ["dconf", "read",
                                "/org/gnome/terminal/legacy/profiles:/list"]
        process = sp.run(get_profiles_command, stdout=sp.PIPE)
        profiles = eval(process.stdout.decode('ascii'))
        return set(profiles)

    @staticmethod
    def set_as_default(profile):
        """
        Sets an existing profile as the default profile
        """
        set_profile_command = ["dconf", "write",
                               "/org/gnome/terminal/legacy/profiles:/default",
                               "\"" + profile + "\""]
        process = sp.run(set_profile_command, stderr=sp.PIPE)
        if process.returncode:
            msg = "Hapycolor encountered an error when running dconf: " \
                    + process.stderr.decode("utf-8")
            raise exceptions.DconfInvalidCommand(msg)

    @staticmethod
    def remove_profile(profile):
        """
        This function is related to :func:`set_as_default` or :func:`get_profiles`,
        but currently, it is only useful for testing purposes.
        """
        remove_command = ["dconf", "reset", "-f",
                          "/org/gnome/terminal/legacy/profiles:/" + profile]
        process = sp.run(remove_command, stderr=sp.PIPE)
        if process.returncode:
            msg = "Hapycolor encountered an error when running dconf: " \
                    + process.stderr
            raise exceptions.DconfInvalidCommand(msg)
