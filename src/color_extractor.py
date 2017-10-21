import utils
import color_filter
import color_reducer
import visual
from ast import literal_eval as make_tuple
import subprocess as sp
import re

class ColorExtractor():

    def __init__(self, image, num_colors):

        self.cf = color_filter.ColorFilter()
        self.cr = color_reducer.ColorReducer()
        self.image = image
        self.num_colors = num_colors
        self.labels = [[15+30*i, 15+30*(i+1)] for i in range(12)]
        self.labels.append([345, 15]) # Special case for red

        # Filter parameters
        self.min_lightness = 0.20
        self.max_lightness = 0.80
        self.min_saturation = 0.10

        # Reduction distance
        self.min_distance = 10

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

        print("ImageMagick colors (" + str(len(magic_colors)) + "):")
        visual.print_palette(magic_colors, size=1)

        # Convert colors to hsl and pick the best ones
        hsl_colors = [utils.rgb_to_hsl(col) for col in magic_colors]

        # Extract the background and foreground
        fg = max(hsl_colors, key=lambda c:c[2])
        bg = min(hsl_colors, key=lambda c:c[2])

        if not self.cf.is_too_dark((bg[0], bg[1], bg[2]*1.0)):
            bg = (0, 0, 0)

        if self.cf.is_too_dark((fg[0], fg[1], fg[2]/2)):
            fg = (0, 0, 1)

        final_colors = {}
        final_colors["wallpaper"] = self.image
        final_colors["special"] = {}
        final_colors["colors"]  = {}
        final_colors["special"]["foreground"] = utils.rgb_to_hex(utils.hsl_to_rgb(fg))
        final_colors["special"]["cursor"]     = utils.rgb_to_hex(utils.hsl_to_rgb(fg))
        final_colors["special"]["background"] = utils.rgb_to_hex(utils.hsl_to_rgb(bg))

        filtered_colors = []
        for col in hsl_colors:
            if not self.cf.is_too_dark(col)              \
                    and not self.cf.is_too_bright(col)   \
                    and self.cf.is_saturated_enough(col):
                filtered_colors.append(col)

        print("Filtered colors (" + str(len(filtered_colors)) + "):")
        visual.print_palette([utils.hsl_to_rgb(c) for c in filtered_colors], size=2)

        # Remove close colors
        reduced_colors = self.cr.color_reducer(filtered_colors, self.min_distance)

        print("Reduced colors (" + str(len(reduced_colors)) + "):")
        visual.print_palette([utils.hsl_to_rgb(c) for c in reduced_colors], size=2)
        # Sort colors by label
        labeled_colors = self.__label_colors(reduced_colors)

        # Pick two colors for each label (if possible)
        for i, l in enumerate(labeled_colors):
            if len(l) >= 2:
                l.sort(key=lambda c: c[2])
                labeled_colors[i] = [max(l[:len(l)//2], key=lambda c: c[1]),
                        max(l[len(l)//2:], key=lambda c: c[1])]

        # Flatten the list and convert colors to rgb format
        all_colors = [col for label in labeled_colors for col in label]
        rgb_colors = [utils.hsl_to_rgb(col) for col in all_colors]

        print("\nColors by label (" + str(len(rgb_colors)) + "):")
        visual.print_palette(rgb_colors, size=2)

        hex_colors = [utils.rgb_to_hex(col) for col in rgb_colors]
        while (len(hex_colors) < 16):
            hex_colors.append(hex_colors[-1])

        for i, c in enumerate(hex_colors):
            final_colors["colors"]["color%s" % i] = c

        return final_colors

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

