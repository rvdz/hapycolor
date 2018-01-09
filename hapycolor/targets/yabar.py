from hapycolor import config
from hapycolor import helpers
from hapycolor import exceptions
from hapycolor import palette as pltte
from . import eight_bit_colors
from . import base
import random, os


class Yabar(base.Target):
    """
        Replace tokens by their defined color in yabar conf file
    """

    tokens = {
              "background":   "$TBG",
              "foreground":   "$TFG",
              "random_color": "$RC"
             }

    configuration_key = "yabar_conf"

    def is_config_initialized():
        try:
            return Yabar.configuration_key in Yabar.load_config()
        except exceptions.InvalidConfigKeyError:
            return False

    def initialize_config():
        p = config.input_path("Path to yabar's custom config file: ")
        if not p.is_file():
            raise exceptions.WrongInputError("Must be a file")

        if not p.is_absolute():
            p = p.resolve()

        Yabar.save_config({Yabar.configuration_key : p.as_posix()})

    def compatible_os():
        return [config.OS.LINUX]

    def export(palette, image_path):
        """
            Parse config file for tokens and replace them
        """
        ya_conf = Yabar.load_config()[Yabar.configuration_key]
        tmp_conf = '~/.tmp_conf'
        with open(ya_conf, 'r') as f:
            with open(tmp_conf, 'a') as tmp:
                body = f.read()
                body = body.replace(Yabar.tokens["background"],
                        helpers.rgb_to_hex(palette._background))
                body = body.replace(Yabar.tokens["foreground"],
                        helpers.rgb_to_hex(palette._foreground))
                index = random.randint(0, len(palette._colors))
                body = body.replace(Yabar.tokens["random_color"],
                        helpers.rgb_to_hex(palette._colors[index]))
                tmp.write(body)

        os.remove(ya_conf)
        os.rename(tmp_conf, ya_conf)
