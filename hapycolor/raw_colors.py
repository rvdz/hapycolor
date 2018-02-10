from hapycolor import palette as pltte
from hapycolor import helpers
from hapycolor import exceptions

import re
import subprocess as sp
from ast import literal_eval as make_tuple


def get(image_path, num_colors):
    """
    Returns a palette filled with colors provided by ImageMagic.
    The foreground (resp. background) is the brightest (resp. darkest)
    color of them.
    """
    magic_proc = sp.Popen(["convert", image_path, "+dither", "-colors",
                           str(num_colors), "-unique-colors", "txt:-"],
                          stdout=sp.PIPE)

    raw_colors = magic_proc.stdout.readlines()

    # Skip the first line which is not a color
    del raw_colors[0]

    # Select only the rgb colors from output
    rgb_colors = [extract_rgb(str(col)) for col in raw_colors]

    palette = pltte.Palette()
    palette.colors = rgb_colors
    palette.foreground, palette.background = get_fg_and_bg(rgb_colors)

    return palette


def extract_rgb(raw_color):
    """
    Checks if the color are encoded over 8 bit (greyscale), 24bit (rgb) or
    32bit (rgb + alpha) and returns a tuple of rgb values

    :param raw_color: en entry line of the result of the imagemagick extraction
    :raises exceptions.BlackAndWhitePictureException: if the colors are encoded
        in a greyscale format.
    :return: A tuple of rgb values
    """
    if re.search("gray", raw_color):
        msg = "Some minimalist hipster thinks he deserves using Hapycolor. " \
                "Fortunately, Hapycolor does not accept b&w images."
        raise exceptions.BlackAndWhitePictureException(msg)
    elif re.search("srgba", raw_color):
        match = re.search("srgba\(.*\)", raw_color).group(0)
        return make_tuple(match[5:])[:-1]
    elif re.search("srgb", raw_color):
        match = re.search("srgb\(.*\)", raw_color).group(0)
        return make_tuple(match[4:])


def get_fg_and_bg(rgb_colors):
    """ Extract the background and foreground """
    hsl_colors = [helpers.rgb_to_hsl(c) for c in rgb_colors]
    fg = max(hsl_colors, key=lambda c: c[2])
    bg = min(hsl_colors, key=lambda c: c[2])

    return helpers.hsl_to_rgb(fg), helpers.hsl_to_rgb(bg)
