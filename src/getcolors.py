from visual import print_palette
from utils import hex_to_rgb
from color_extractor import ColorExtractor
from PIL import Image, ImageDraw
import argparse
import config
import unittest
import sys

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
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--file", help="File path to the image", required=False)
    args = vars(ap.parse_args())

    extractor = ColorExtractor(args["file"], num_colors=200)
    colors = extractor.get_colors()
    rgbcols = [hex_to_rgb(col) for col in colors]
    print("\nFinal palette (" + str(len(rgbcols)) + "):")
    print_palette(rgbcols, size=2)
    colors_to_file(colors, "palette.png")
