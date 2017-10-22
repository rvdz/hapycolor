"""

888   |                              e88~-_           888
888___|   /~~~8e  888-~88e  Y88b  / d888   \  e88~-_  888  e88~-_  888-~_
888   |       88b 888  888b  Y888/  8888     d888   i 888 d888   i 888
888   |  e88~-888 888  8888   Y8/   8888     8888   | 888 8888   | 888
888   | C888  888 888  888P    Y    Y888   / Y888   | 888 Y888   | 888
888   |  \88_-888 888-_88/    /      \88_-~   \88_-~  888  \88_-~  888
                  888       _/

"""

from . import config
from . import visual
from . import helpers
from .color import extractor

from PIL import Image, ImageDraw
import argparse

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

def main(args=None):

    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--file", help="File path to the image", required=True)
    args = vars(ap.parse_args())

    config.init_configs()

    colors = extractor.Extractor(args["file"], num_colors=250).get_colors()

    name = colors["wallpaper"].split("/")[-1].split(".")[0]
    for f in config.export_functions():
        f(colors, name)

    print("\nFinal palette (" + str(len(colors["colors"])) + "):")
    visual.print_palette(colors["colors"], size=2)

    print("\Foreground color:")
    visual.print_palette([colors["foreground"]], size=4)

    print("\Background color:")
    visual.print_palette([colors["background"]], size=4)

    colors_to_file([c for c in colors["colors"]], "palette.png")
    helpers.save_json("palette.json", colors["colors"])

if __name__ == '__main__':
    main()
