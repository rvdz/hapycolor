from hapycolor import helpers
from hapycolor import exceptions
from hapycolor import targets
from hapycolor import palette as pltte
from hapycolor.configuration_editor import ConfigurationEditor
from . import eight_bit_colors
from . import base
import random
import os
import re


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
            Parse config file for macros and replace the targeted colors
        """
        ya_conf    = Yabar.load_config()[Yabar.configuration_key]
        with open(ya_conf, 'r') as ya_file:
            configuration = ya_file.read().splitlines()

        configuration = ConfigurationEditor(configuration).replace(palette)

        with open(ya_conf, 'w') as ya_file:
            ya_file.write('\n'.join(configuration))
