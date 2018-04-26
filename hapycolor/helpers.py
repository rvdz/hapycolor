import json
import re
import readline
from hapycolor import exceptions
import os
import pathlib

""" Utilitary methods to convert color types  """


def is_hex(color):
    return re.match(r"0[xX][0-9a-fA-F]{6}", color) is not None


def can_be_hsl(color):
    if color.__class__ != tuple or len(color) != 3:
        return False
    if (0 <= color[0] and color[0] < 360)         \
            and (0 <= color[1] and color[1] <= 1) \
            and (0 <= color[2] and color[2] <= 1):
        return True
    return False


def can_be_rgb(color):
    if color.__class__ != tuple or len(color) != 3:
        return False
    if all([(0 <= e and e <= 255) and (e.__class__ == int) for e in color]):
        return True
    return False


def contrast(rgbcolor):
    return (299*rgbcolor[0] + 587*rgbcolor[1] + 114*rgbcolor[2]) / 1000


def contrast_norm(rgbcol1, rgbcol2):
    return abs(contrast(rgbcol1) - contrast(rgbcol2))


def rgb_to_hex(colrgb):
    if not can_be_rgb(colrgb):
        raise exceptions.ColorFormatError("The input color must be defined in"
                                          + " the rgb base")
    return '#%02x%02x%02x' % (colrgb[0], colrgb[1], colrgb[2])


def hex_to_rgb(hexcol):
    h = hexcol.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def hsl_to_hex(colhsl):
    colrgb = hsl_to_rgb(colhsl)
    return rgb_to_hex(colrgb)


def rgb_to_hsl(colrgb):
    if not can_be_rgb(colrgb):
        raise exceptions.ColorFormatError("The input color: " + str(colrgb)
                                          + " must be defined in the rgb base")
    r = colrgb[0] / 255.
    g = colrgb[1] / 255.
    b = colrgb[2] / 255.
    maxrgb = float(max(r, g, b))
    minrgb = float(min(r, g, b))
    luminosity = (minrgb + maxrgb) / 2
    if minrgb == maxrgb:
        return 0, 0.0, luminosity

    if luminosity <= 0.5:
        s = (maxrgb - minrgb) / (maxrgb + minrgb)
    else:
        s = (maxrgb - minrgb) / (2 - maxrgb - minrgb)

    if maxrgb == r:
        h = (g - b) / (maxrgb - minrgb)
    elif maxrgb == g:
        h = 2 + (b - r) / (maxrgb - minrgb)
    else:
        h = 4 + (r - g) / (maxrgb - minrgb)
    h = int(round(h * 60)) % 360
    return h, s, luminosity


def hsl_to_rgb(colhsl):
    h, s, lum = colhsl
    h /= 360.
    if s == 0:
        return (int(round(255 * lum)),) * 3
    if lum < 0.5:
        tmp1 = lum * (1 + s)
    else:
        tmp1 = lum + s - (lum * s)
    tmp2 = 2*lum - tmp1
    tmpr = h + 1/3. if h <= 2/3. else h - 2/3.
    tmpg = h
    tmpb = h - 1/3. if h >= 1/3. else h + 2/3.
    return (_tmpcolor(tmpr, tmp1, tmp2),
            _tmpcolor(tmpg, tmp1, tmp2),
            _tmpcolor(tmpb, tmp1, tmp2))


def _tmpcolor(tmpc, tmp1, tmp2):
    if 6 * tmpc < 1:
        c = tmp2 + tmpc*6*(tmp1 - tmp2)
    elif 2 * tmpc < 1:
        c = tmp1
    elif 3 * tmpc < 2:
        c = tmp2 + (tmp1 - tmp2)*(2/3. - tmpc) * 6
    else:
        c = tmp2
    return int(round(255 * c))


def load_json(file_path):
    with open(file_path) as f:
        data = json.load(f)
    return data


def save_json(data_file, data_object):
    with open(data_file, 'w') as f:
        json.dump(data_object, f, indent=4)


def update_json(data_file, data_object):
    if not os.path.exists(data_file):
        with open(data_file, 'wt') as inFile:
            inFile.write("{}")
        data = data_object
    else:
        with open(data_file) as f:
            data = json.load(f)
        data.update(data_object)

    with open(data_file, 'w') as f:
        json.dump(data, f, indent=2)


def input_path(prompt_str):
    """
    Prompts the user with a string and returns a :class:`pathlib.Path` from the
    user's input:

    :arg prompt_str: the string to display before the user's entry
    """
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(readline.get_completer())
    return pathlib.Path(input(prompt_str)).expanduser()
