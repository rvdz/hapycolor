from colormath.color_objects import LabColor, sRGBColor, HSLColor
from colormath.color_conversions import convert_color

""" Utilitary methods to convert color types  """

def contrast(rgbcolor):
    return (299*rgbcolor[0] + 587*rgbcolor[1] + 114*rgbcolor[2]) / 1000

def contrast_norm(rgbcol1, rgbcol2):
    return abs(contrast(rgbcol1) - contrast(rgbcol2))

def rgb_to_hex(colrgb):
    return '#%02x%02x%02x' % (colrgb[0], colrgb[1], colrgb[2])

def hex_to_rgb(hexcol):
    h = hexcol.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2 ,4))

def hsl_to_hex(colhsl):
    colrgb = hsl_to_rgb(colhsl)
    return rgb_to_hex(colrgb)

def rgb_to_hsl(colrgb):
    r = colrgb[0] / 255.
    g = colrgb[1] / 255.
    b = colrgb[2] / 255.
    maxrgb = float(max(r,g,b))
    minrgb = float(min(r,g,b))
    l = (minrgb + maxrgb) / 2
    if minrgb == maxrgb:
        return 0, 0.0, l

    if l <= 0.5:
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
    return h, s, l

def hsl_to_rgb(colhsl):
    h, s, l = colhsl
    h /= 360.
    if s == 0:
        return (int(round(255 * l)),) * 3
    if l < 0.5:
        tmp1 = l * (1+s)
    else:
        tmp1 = l+s - l*s
    tmp2 = 2*l - tmp1
    tmpr = h + 1/3. if h <= 2/3. else h - 2/3.
    tmpg = h
    tmpb = h - 1/3. if h >= 1/3. else h + 2/3.
    return (_tmpcolor(tmpr,tmp1,tmp2), _tmpcolor(tmpg,tmp1,tmp2), _tmpcolor(tmpb,tmp1,tmp2))

def _tmpcolor(tmpc, tmp1, tmp2):
    if 6*tmpc < 1:
        c = tmp2 + tmpc*6*(tmp1 - tmp2)
    elif 2*tmpc < 1:
        c = tmp1
    elif 3*tmpc < 2:
        c = tmp2 + (tmp1 - tmp2)*(2/3. - tmpc)*6
    else:
        c = tmp2
    return int(round(255*c))

def hsl_to_lab(colhsl):
    hsl = HSLColor(colhsl[0], colhsl[1], colhsl[2])
    return convert_color(hsl, LabColor).get_value_tuple()

def lab_to_hsl(collab):
    lab = LabColor(collab[0], collab[1], collab[2])
    return convert_color(lab, HSLColor).get_value_tuple()
