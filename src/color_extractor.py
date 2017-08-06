from utils import contrast_norm, rgb_to_hex, rgb_to_hsl, hsl_to_rgb
from visual import print_palette
from ast import literal_eval as make_tuple
import subprocess as sp
import re

class ColorExtractor():

    def __init__(self, image, num_colors):
        self.image = image
        self.num_colors = num_colors
        self.min_lightness = 0.20
        self.max_lightness = 0.80
        self.min_saturation = 0.10
        self.labels = [[15+30*i, 15+30*(i+1)] for i in range(12)]
        self.labels.append([345, 15]) # Special case for red

    def get_colors(self):
        """ This method tries to extract the most various colors in an image
            using several filters """

        # Get the prominent colors from the image with imagemagick
        magic_proc = sp.Popen(["convert", self.image, "+dither", "-colors",
            str(self.num_colors), "-unique-colors", "txt:-"],
            stdout=sp.PIPE)
        raw_colors = magic_proc.stdout.readlines()

        # Skip the first line which is not a color
        del raw_colors[0]

        # Select only the rgb colors from output
        magic_colors = [re.search("rgb\(.*\)", str(col)).group(0)[3:] for col in raw_colors]
        magic_colors = [make_tuple(rgb_col) for rgb_col in magic_colors]

        print "ImageMagick colors"
        print_palette(magic_colors, size=1)

        # Convert colors to hsl and pick the best ones
        hsl_colors = [rgb_to_hsl(col) for col in magic_colors]
        good_colors = []
        for col in hsl_colors:
            if col[2] >= self.min_lightness\
                    and col[2] <= self.max_lightness\
                    and col[1] >= self.min_saturation:
                good_colors.append(col)

        # Sort colors by label
        labeled_colors = self.__label_colors(good_colors)

        # Pick two colors for each label (if possible)
        for i, l in enumerate(labeled_colors):
            if len(l) >= 2:
                l.sort(key=lambda c: c[2])
                labeled_colors[i] = [max(l[:len(l)/2], key=lambda c: c[1]),
                        max(l[len(l)/2:], key=lambda c: c[1])]

        # Flatten the list and convert colors to rgb format
        all_colors = [col for label in labeled_colors for col in label]
        rgb_colors = [hsl_to_rgb(col) for col in all_colors]

        print "\nColors by label"
        print_palette(rgb_colors, size=2)

        diff_contrast = 30
        i = 0
        while i < len(rgb_colors)-1:
            if contrast_norm(rgb_colors[i], rgb_colors[i+1]) < diff_contrast:
                rgb_colors.remove(rgb_colors[i+1])
                i -= 1
            else:
                i += 1

        hex_colors = [rgb_to_hex(col) for col in rgb_colors]
        return hex_colors

    def __label_colors(self, colors):
        """ Sort colors by labels """
        labeled_colors = [[] for k in range(12)]
        for col in colors:
            id_label = self.__find_label(col)
            labeled_colors[id_label].append(col)
        return labeled_colors

    def __find_label(self, hslcol):
        for i, l in enumerate(self.labels):
            if hslcol[0] >= l[0] and hslcol[0] < l[1]:
                return i
        return -1

