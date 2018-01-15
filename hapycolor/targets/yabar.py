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

        RGB colors must be written as 0x$TOKEN
        ARGB colors must be written as 0xA$TOKEN
        where:
            - A is the hex alpha value (00 - FF)
            - TOKEN is defined below (TGB, TFG, etc.)

        !! The defined color token MUST be followed by the color number
        !! If it does not exist, it uses the first one
        !! Color number range is 0 - 15
    """

    tokens = {
              "background":    "$TBG",
              "foreground":    "$TFG",
              "random_color":  "$RC",
              "defined_color": "$DC"
             }

    max_colors = 15

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
        tmp_conf = '/tmp/tmp.conf'
        with open(ya_conf, 'r') as f:
            with open(tmp_conf, 'a') as tmp:
                body = f.read()
                body = body.replace(Yabar.tokens["background"],
                        helpers.rgb_to_hex(palette._background)[1:])

                body = body.replace(Yabar.tokens["foreground"],
                        helpers.rgb_to_hex(palette._foreground)[1:])

                occurences = body.count(Yabar.tokens["random_color"])
                indexes = [i for i in range(len(palette._colors))]
                for i in range(occurences):
                    i_index = random.randint(0, len(indexes)-1)
                    index = indexes[i_index]
                    del indexes[i_index]
                    body = body.replace(Yabar.tokens["random_color"],
                            helpers.rgb_to_hex(palette._colors[index])[1:], 1)

                for i in range(max_colors):
                    if max_colors > len(palette._colors):
                        color = helpers.rgb_to_hex(palette._colors[0])[1:]
                    else:
                        color = helpers.rgb_to_hex(palette._colors[i])[1:]
                    body = body.replace(Yabar.tokens["defined_color"]+str(i), color)

                tmp.write(body)
        os.remove(ya_conf)
        os.rename(tmp_conf, ya_conf)
