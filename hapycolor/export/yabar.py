from hapycolor import config
from hapycolor import helpers

class Yabar:

    @staticmethod
    def profile(palette, name):
        """
            Creates a new yabar config file
        """

        colors = map(lambda x: rgb_to_hex, palette['colors'])
        fg = rgb_to_hex(palette['foreground'])
        bg = rgb_to_hex(palette['background'])

        with open(config.yabar(), 'w+') as f:
            f.close()
