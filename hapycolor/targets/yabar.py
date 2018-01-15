from hapycolor import config
from hapycolor import helpers
from hapycolor import exceptions
from hapycolor import palette as pltte
from . import eight_bit_colors
from . import base
import random, os, re


class Yabar(base.Target):


    """
        Replace tokens by their defined color in yabar conf file

        RGB colors must be written as 0x$TOKEN
        ARGB colors must be written as 0xA$TOKEN
        where:
            - A is the hex alpha value (00 - FF)
            - TOKEN is defined below (TGB, TFG, etc.)

        Methods for defined color:
            - 'closest': finds the closest color in hue
                         => full token must look like '$DC30T60'
                         for hue from 30 to 60
            - 'range': finds a color in the hue range, if none,
                       uses the default hue
                       => full token must be '$DCT45' for a target
                       hue of 45
        !!! THE TOKEN DEFINES THE METHOD !!!
    """

    tokens = {
              "background":    "$TBG",
              "foreground":    "$TFG",
              "random_color":  "$RC",
              "defined_color": "$DC"
             }

    max_colors = 15

    configuration_key = "yabar_conf"
    configuration_hue_key = "yabar_default_hue"


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

        p = input("Default hue for defined colors: ")

        try:
            if not 0 <= int(p) <= 360:
                raise exceptions.WrongInputError("Must be an int")
        except:
            raise exceptions.WrongInputError("Must be an int")

        Yabar.save_config({Yabar.configuration_hue_key: p})

    def compatible_os():

        return [config.OS.LINUX]

    def export(palette, image_path):

        """
            Parse config file for tokens and replace them
        """

        ya_conf    = Yabar.load_config()[Yabar.configuration_key]
        def_hue    = int(Yabar.load_config()[Yabar.configuration_hue_key])
        tmp_conf   = '/tmp/tmp.conf'
        col_bg     = helpers.rgb_to_hex(palette._background)[1:]
        col_fg     = helpers.rgb_to_hex(palette._foreground)[1:]
        hex_colors = list(map(lambda x: helpers.rgb_to_hex(x)[1:],
                              palette._colors))
        hsl_colors = list(map(lambda x: helpers.rgb_to_hsl(x),
                              palette._colors))

        with open(ya_conf, 'r') as f, open(tmp_conf, 'a') as tmp:
            body = f.read()

            # TOKEN BACKGROUND
            body = body.replace(Yabar.tokens["background"], col_bg)

            # TOKEN FOREGROUND
            body = body.replace(Yabar.tokens["foreground"], col_fg)

            # TOKEN RANDOM COLOR
            occurences = body.count(Yabar.tokens["random_color"])
            indexes = [i for i in range(len(hex_colors))]
            for i in range(occurences):
                i_index = random.randint(0, len(indexes) - 1)
                index = indexes[i_index]
                del indexes[i_index]
                body = body.replace(Yabar.tokens["random_color"],
                                    hex_colors[index], 1)

            # TOKEN DEFINED COLOR
            # Range method
            regex = re.compile("\$DC\d+T\d+")
            matches = regex.findall(body)
            def_dists = list(map(lambda x: abs(def_hue - x[0]), hsl_colors))
            def_col = hex_colors[def_dists.index(min(def_dists))]
            for match in matches:
                regex = re.compile(r"\d+")
                hrange = regex.findall(match)
                hstart, hend = int(hrange[0]), int(hrange[1])
                for c in hsl_colors:
                    if hstart < c[0] < hend:
                        body = body.replace(match, helpers.hsl_to_hex(c)[1:])
                        break
                else:
                    body = body.replace(match, def_col)

            # Closest method
            regex = re.compile("\$DCT\d+")
            matches = regex.findall(body)
            for match in matches:
                regex = re.compile(r"\d+")
                target_hue = int(regex.findall(match)[0])
                dists = list(map(lambda x: min(abs(target_hue - x[0]),
                                 abs(abs(target_hue - x[0]) - 360)),
                                 hsl_colors))
                index = dists.index(min(dists))
                body = body.replace(match, hex_colors[index])

            tmp.write(body)
        os.remove(ya_conf)
        os.rename(tmp_conf, ya_conf)
