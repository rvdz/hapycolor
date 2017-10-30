# TODO: Find a synonym of filter
from hapycolor import helpers
from hapycolor import visual

from hapycolor import exceptions

from . import filter as fltr
from . import reducer
from hapycolor import palette

from ast import literal_eval as make_tuple

import pathlib
import re
import subprocess as sp

class Extractor():
    def __init__(self, image, num_colors):

        if num_colors.__class__ != int:
            raise exceptions.ExtractorArgumentsError("Function requires: num_colors.__class__ == int")

        if num_colors <= 0:
            raise exceptions.ExtractorArgumentsError("Requires more than zero colors")

        try:
            path = pathlib.Path(image).resolve()
        except TypeError as e:
            raise exceptions.ExtractorArgumentsError("Given path argument is not a string", e)

        if not path.is_file():
            raise exceptions.InvalidImageError("Provided path does not point to a file: " \
                                            + path.as_posix())

        self.cf         = fltr.Filter()
        self.cr         = reducer.Reducer()
        self.image      = image
        self.num_colors = num_colors

        # Filter parameters
        self.min_lightness  = 0.20
        self.max_lightness  = 0.80
        self.min_saturation = 0.10

        # Reduction distance
        self.min_distance = 10

    def __get_magic_colors(self):
        """ Get the prominent colors from the image with imagemagick. Returns an array of rgb tuples """
        magic_proc = sp.Popen(["convert", self.image, "+dither", "-colors",
            str(self.num_colors), "-unique-colors", "txt:-"],
            stdout=sp.PIPE)
        raw_colors = magic_proc.stdout.readlines()

        # Skip the first line which is not a color
        del raw_colors[0]

        # Select only the rgb colors from output
        magic_colors = [re.search("rgb\(.*\)", str(col)).group(0)[3:] for col in raw_colors]
        return [make_tuple(rgb_col) for rgb_col in magic_colors]

    def __get_fg_and_bg(self, hsl_colors):
        """ Extract the background and foreground """
        fg = max(hsl_colors, key=lambda c:c[2])
        bg = min(hsl_colors, key=lambda c:c[2])

        if not self.cf.is_too_dark((bg[0], bg[1], bg[2]*1.0)):
            bg = (0, 0, 0)

        if self.cf.is_too_dark((fg[0], fg[1], fg[2]/2)):
            fg = (0, 0, 1)

        return helpers.hsl_to_rgb(fg), helpers.hsl_to_rgb(bg)

    def get_colors(self):
        """ This method tries to extract the most various colors in an image
            using several filters. It returns an instance of the class 'Palette' """

        magic_colors = self.__get_magic_colors()

        print("ImageMagick colors (" + str(len(magic_colors)) + "):")
        visual.print_palette(magic_colors, size=1)

        # Convert colors to hsl and pick the best ones
        hsl_colors = [helpers.rgb_to_hsl(col) for col in magic_colors]

        final_colors = palette.Palette()
        final_colors.foreground, final_colors.background = self.__get_fg_and_bg(hsl_colors)

        filtered_magic = magic_colors[:]
        filtered_colors = []

        for i, col in enumerate(hsl_colors):
            if not self.cf.is_too_dark(col)              \
                    and not self.cf.is_too_bright(col)   \
                    and self.cf.is_saturated_enough(col):
                filtered_colors.append(col)
            else:
                filtered_magic[i] = (0,0,0)

        print("\nFiltered colors (" + str(len(filtered_colors)) + "):")
        visual.print_palette(filtered_magic, size=1)

        # Remove close colors
        reduced_colors = self.cr.reduce(filtered_colors, self.min_distance)

        print("\nReduced colors (" + str(len(reduced_colors)) + "):")
        visual.print_palette([helpers.hsl_to_rgb(c) for c in reduced_colors], size=2)

        # Sort by hue
        # sorted_hsl_colors = sort(reduced_colors, lambda c : c[0])
        # sorted_colors = [helpers.hsl_to_rgb(c) for c in sorted_hsl_colors]

        # Sort colors by label
        # hsl_labeled_colors = self.__label_colors(reduced_colors)
        # labeled_colors = []
        # for label in hsl_labeled_colors:
        #     labeled_colors.append([helpers.hsl_to_rgb(c) for c in label])
        #print("Labels :")
        #for i, l in enumerate(labeled_colors):
        #    visual.print_palette([helpers.hsl_to_rgb(c) for c in l], size=1)

        # Flatten the list and convert colors to rgb format
        # all_colors = [col for label in labeled_colors for col in label]
        # rgb_colors = [helpers.hsl_to_rgb(col) for col in all_colors]
        #print("\nColors by label (" + str(len(rgb_colors)) + "):")
        #visual.print_palette(rgb_colors, size=2)

        # Ensure that the final palette contains at least 16 colors
        # FIXME to be improved, we could repeat different colors from different label
        # instead of just the last one
        # while (len(rgb_colors) < 16):
        #     rgb_colors.append(rgb_colors[-1])

        # TODO: What do we do if there are n > 16 colors?
        # if len(rgb_colors) > 16:
        #     final_colors.colors = rgb_colors[:16]
        # else:
        #     final_colors.colors = rgb_colors[:]
        final_colors.colors = [helpers.hsl_to_rgb(c) for c in reduced_colors]
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
