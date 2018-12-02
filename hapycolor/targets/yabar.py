import tempfile
import random
import os
import re
import PIL.Image
import numpy as np
from hapycolor import helpers
from hapycolor import exceptions
from hapycolor import targets
from hapycolor import palette as pltte
from hapycolor.configuration_editor import ConfigurationEditor
from . import eight_bit_colors
from . import base


class Yabar(base.Target):
    configuration_key = "yabar_conf"

    def is_config_initialized():

        try:
            return Yabar.configuration_key in Yabar.load_config()
        except exceptions.InvalidConfigKeyError:
            return False

    def initialize_config():

        p = helpers.input_path("Path to yabar's custom config file: ")

        if not p.is_file():
            raise exceptions.WrongInputError("Must be a file")
        if not p.is_absolute():
            p = p.resolve()

        Yabar.save_config({Yabar.configuration_key: p.as_posix()})

    def compatible_os():

        return [targets.OS.LINUX]

    def export(palette, image_path):
        """
        Parse config file for macros and replace the targeted colors.
        In addition, it will evaluate the average luminosity of the top
        5% of the image and choose an appropriate text foreground color.
        """
        avg_luminosity = Yabar.get_top_luminosity(image_path)
        foreground = (255, 255, 255) if avg_luminosity < 0.5 else (0, 0, 0)
        palette.other["yabar_foreground"] = foreground

        yabar_config = Yabar.load_config()[Yabar.configuration_key]
        Yabar.update_config(palette, yabar_config)

    @staticmethod
    def update_config(palette, yabar_config):
        with open(yabar_config, 'r') as ya_file:
            configuration = ya_file.read().splitlines()

        configuration = ConfigurationEditor(configuration).replace(palette)

        with open(yabar_config, 'w') as ya_file:
            ya_file.write('\n'.join(configuration))

    @staticmethod
    def get_top_luminosity(image_path):
        """
        Returns the average luminosity of the top 10% section
        of the image.
        """
        crop_ratio = 0.05
        im = PIL.Image.open(image_path)
        height, width = im.size
        cropped_height = int(height * crop_ratio)
        im = im.crop((0, 0, width, cropped_height))
        pixels = list(im.getdata())
        luminosities = [helpers.rgb_to_hsl(rgb)[2] for rgb in pixels]
        return np.average(luminosities)
