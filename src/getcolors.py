from utils import contrast_norm
from PIL import Image, ImageDraw
from utils import rgb_to_hex, hsl_to_hex, rgb_to_hsl, hsl_to_rgb
from ast import literal_eval as make_tuple
import subprocess as sp
import re
import sys


# The color must be in HSL format
def find_label(col, labels):
    for i, l in enumerate(labels):
        if col[0] >= l[0] and col[0] < l[1]:
            return i
    return -1

def get_colors(infile, outfile, numcolors=10, swatchsize=20, resize=150):

    color_labels = [[15+30*i, 15+30*(i+1)] for i in range(12)] # Color intervals (e.g. red, cyan)
    color_labels.append([345, 15]) # Special case for red

    # Needed for quality magic stuffs
    magic_proc = sp.Popen(["convert", infile, "+dither", "-colors",
        str(numcolors), "-unique-colors", "txt:-"],
        stdout=sp.PIPE)
    raw_colors = magic_proc.stdout.readlines()
    del raw_colors[0] # Skip the first line which is not a color
    magic_colors = [re.search("rgb\(.*\)", str(col)).group(0)[3:] for col in raw_colors]
    magic_colors = [make_tuple(rgb_col) for rgb_col in magic_colors]

    hsl_colors = [rgb_to_hsl(col) for col in magic_colors]

    # Minimum lightness
    min_lightness = 0.20
    max_lightness = 0.80

    bgcolor = min(hsl_colors, key=lambda tup: tup[2])
    good_colors = [col for col in hsl_colors if col[2] >= min_lightness and col[2] <= max_lightness]
    fgcolor = max(good_colors, key=lambda tup: tup[2])
    good_colors = [col for col in good_colors if col[1] > 0.1]
    labeled_colors = [[] for k in range(12)]

    # Sort colors by label
    for col in good_colors:
        id_label = find_label(col, color_labels)
        labeled_colors[id_label].append(col)

    # Pick two colors for each label (if possible)
    for i, l in enumerate(labeled_colors):
        if len(l) >= 2:
            l.sort(key=lambda c: c[2])
            labeled_colors[i] = [max(l[:len(l)/2], key=lambda c: c[1]),
                    max(l[len(l)/2:], key=lambda c: c[1])]

    all_colors = [col for label in labeled_colors for col in label] # Flattens the list
    rgb_colors = [hsl_to_rgb(col) for col in all_colors]
    diff_contrast = 30
    i = 0
    while i < len(rgb_colors)-1:
        if contrast_norm(rgb_colors[i], rgb_colors[i+1]) < diff_contrast:
            rgb_colors.remove(rgb_colors[i+1])
            i -= 1
        else:
            i += 1

    #hsl_saturation.sort(key=lambda c: c[1])

    hex_colors = [rgb_to_hex(col) for col in rgb_colors]
    hex_colors.append(hsl_to_hex(fgcolor))
    #for col in hsl_saturation:
    #    print(str(col) + ", sat = " + str(col[1]))
    #random.shuffle(hex_colors)
    hex_colors = [hsl_to_hex(bgcolor)] + hex_colors

    return hex_colors

def colors_to_file(colors, filename, resize=150, swatchsize=20):
    """ Creates a color palette and saves it to file """
    pal = Image.new('RGB', (swatchsize*len(colors) + 10, swatchsize))
    draw = ImageDraw.Draw(pal)

    posx = 0
    i = 1
    for col in colors:
        draw.rectangle([posx, 0, posx+swatchsize, swatchsize], fill=col)
        posx = posx + swatchsize
        i += 1

    del draw
    pal.save(filename, "PNG")

if __name__ == '__main__':
    colors = get_colors(sys.argv[1], 'new_palette_color.png', numcolors=500)
    for col in colors:
        print(col)
    colors_to_file(colors, "palette.png")
