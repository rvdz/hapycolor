from hapycolor import config
from hapycolor import exceptions
from hapycolor.helpers import rgb_to_hex
from hapycolor import palette as pltte
from . import base

import subprocess, sys, os


class Gnome(base.Target):


    """
        Creates a Gnome-Terminal theme

        Erases the default one if it has not been changed
        Otherwise appends a new one to the list
    """

    configuration_key = "gnome_terminal_profiles"

    def initialize_config():
        """
            Set the path for themes
        """
        default_path = '/org/gnome/terminal/legacy/profiles:'
        p = config.input_path("Path to gnome-terminal's dconf profiles\n(Keep empty to use default path '{}'): ".format(default_path))
        if str(p) == '.':
            Gnome.save_config({Gnome.configuration_key : default_path})
            return

        if str(p)[-1] != ':':
            raise exceptions.WrongInputError("Must end with ':'")

        Gnome.save_config({Gnome.configuration_key : str(p)})

    def is_config_initialized():
        try:
            is_init = Gnome.configuration_key in Gnome.load_config()
        except exceptions.InvalidConfigKeyError:
            return False
        return is_init

    def compatible_os():
        return [config.OS.LINUX]

    def export(palette, image_path):
        """
            Creates a Gnome Terminal profile
            Requires a 18 colors palette in rgb format
        """

        if palette.__class__ != pltte.Palette:
            msg = "The palette does not respect the appropriate structure"
            raise exceptions.PaletteFormatError(msg)

        name = os.path.splitext(os.path.basename(image_path))[0]
        saved_profiles_path = Gnome.load_config()[Gnome.configuration_key]
        colors = list(map(lambda x: rgb_to_hex(x)[1:], palette._colors))
        fg = rgb_to_hex(palette._foreground)[1:]
        bg = rgb_to_hex(palette._background)[1:]

        open('./tmp', 'a').close()
        with open('./tmp', 'w') as f:
            f.write('%s\n' % bg)
            f.write('%s\n' % fg)
            for c in colors:
                f.write('%s\n' % c)
            f.close()

        process = subprocess.Popen(['bash',  './hapycolor/targets/export_gnome.sh', name, './tmp', saved_profiles_path], stdout=subprocess.PIPE, bufsize=1)
        with process.stdout:
            for line in iter(process.stdout.readline, b''):
                print(line, )
        process.wait()
