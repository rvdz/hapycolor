import pathlib
import enum
from os import listdir
from hapycolor import helpers
from hapycolor import targets
from hapycolor import exceptions
from hapycolor.targets import base
from hapycolor import targets
from hapycolor.configuration_editor import ConfigurationEditor


class Rofi(base.Target):
    """
    To run `rofi` with the generated profile, execute
    `rofi -run --config ~/.config/hapycolor.rasi`.

    When configuring this target, the user will be prompted about which
    configuration template to use. This version of hapycolor prefers using
    templates instead of letting the user directly provide a configuration
    file with hapycolor's macros since some effort is required in order to
    understand how the configuration interacts with the end result. So, it
    seemed more interesting using templates that already contain color
    macros. If a user wants to add his own templates, this can be done just
    by adding the file into `./hapycolor/targets/rofi/`.
    """

    configuration_path = "~/.config/hapycolor.rasi"
    configuration_key = "configuration"
    template_key = "template"

    ThemeEnum = enum.Enum("ThemeEnum",
                          [(t.split('.')[0].upper(),
                            "hapycolor/targets/rofi/" + t)
                           for t in listdir("./hapycolor/targets/rofi") if ".rasi" in t])

    @staticmethod
    def is_config_initialized():
        try:
            return Rofi.configuration_key in Rofi.load_config()
        except exceptions.InvalidConfigKeyError:
            return False

    @staticmethod
    def compatible_os():
        return [targets.OS.LINUX]

    @staticmethod
    def initialize_config():
        """
        Currently, Rofi will write a configuration file in:
        `~/.config/hapycolor.rasi`. In addition, when configuring thistarget,
        the user will be prompted about which configuration template to use.
        """
        Rofi.save_config({Rofi.configuration_key: Rofi.configuration_path})

        theme = select_theme()

        Rofi.save_config({Rofi.template_key: theme.value})

    @staticmethod
    def select_theme():
        try:
            print("\nSelect a theme:")
            for i, t in enumerate(Rofi.ThemeEnum):
                print("{}: ({})".format(t.name, i))
            theme_i = int(input("Theme: "))
            if 0 <= theme_i < len(Rofi.ThemeEnum):
                return list(Rofi.ThemeEnum)[theme_i]
            else:
                raise ValueError
        except ValueError:
            print("Value must be an integer between 0 and {}" \
                  .format(len(Rofi.ThemeEnum)))
            return Rofi.select_theme()

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
            config_file.write('\n'.join(filled_template))
