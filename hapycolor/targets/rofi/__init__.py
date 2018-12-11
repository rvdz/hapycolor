import pathlib
import enum
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
    configuration template to use.

    This version of hapycolor prefers using templates instead of letting the
    user directly provide a configuration file with hapycolor's macros since
    some effort is required in order to understand how the configuration
    interacts with the end result. So, it seemed more interesting using
    templates that already contain color macros. If a user wants to add his
    own templates, this can be done just by adding the file with a '.rasi'
    extension into `./hapycolor/targets/rofi/`.

    Currently supported themes:

    - Monokai
    - lb
    - arc-red-dark

    """

    configuration_path = "~/.config/hapycolor.rasi"
    configuration_key = "configuration"
    template_key = "template"

    @staticmethod
    def is_config_initialized():
        try:
            expected = {Rofi.configuration_key, Rofi.template_key}
            return expected.issubset(set(Rofi.load_config()))
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
        Rofi.save_config({Rofi.configuration_key:
                          pathlib.Path(Rofi.configuration_path).expanduser()})

        theme = Rofi.select_theme()

        Rofi.save_config({Rofi.template_key: theme.value})

    @staticmethod
    def select_theme():
        rofi_dir = pathlib.Path(__file__).parent
        rasi_files = [t for t in rofi_dir.iterdir() if ".rasi" == t.suffix]
        theme_enum = enum.Enum("ThemeEnum", [(t.stem.upper(), t.as_posix())
                                            for t in rasi_files])

        try:
            print("\nSelect a theme:")
            for i, t in enumerate(theme_enum):
                print("{}: ({})".format(t.name, i))
            theme_i = int(input("Theme: "))
            if 0 <= theme_i < len(theme_enum):
                return list(theme_enum)[theme_i]
            else:
                raise ValueError
        except ValueError:
            print("Value must be an integer between 0 and {}" \
                  .format(len(theme_enum)))
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
