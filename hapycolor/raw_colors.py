from hapycolor import palette as pltte
from hapycolor import helpers

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
    magic_colors = [re.search("rgb\(.*\)", str(col)).group(0)[3:] for col in raw_colors]
    rgb_colors = [make_tuple(rgb_col) for rgb_col in magic_colors]

    palette = pltte.Palette()
    palette.colors = rgb_colors
    palette.foreground, palette.background = get_fg_and_bg(rgb_colors)

    return palette

def get_fg_and_bg(rgb_colors):
    """ Extract the background and foreground """
    hsl_colors = [helpers.rgb_to_hsl(c) for c in rgb_colors]
    fg = max(hsl_colors, key=lambda c: c[2])
    bg = min(hsl_colors, key=lambda c: c[2])

    return helpers.hsl_to_rgb(fg), helpers.hsl_to_rgb(bg)
