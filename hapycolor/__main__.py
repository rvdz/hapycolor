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
from . import targets
from . import raw_colors
from . import filters

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


def parse_arguments():
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--file", help="File path to the image")
    ap.add_argument("-d", "--dir", help="File directory to the image "
            + "(this option will NOT export variables, use -f instead).")
    ap.add_argument("-j", "--json", help="Saves output as a Json format "
            + " and do not export variables")
    args = vars(ap.parse_args())
    if not (args.file or args.dir):
        ap.error('No action requested, add -f or -d')
    return args

def display_palette(palette):
    print("\nFinal palette (" + str(len(palette.colors)) + "):")
    visual.print_palette(palette.colors, size=2)

    print("\Foreground color:")
    visual.print_palette([palette.foreground], size=4)

    print("\Background color:")
    visual.print_palette([palette.background], size=4)

    colors_to_file([c for c in palette.colors], "palette.png")
    helpers.save_json("palette.json", palette.colors)


def main(args=None):

    args = parse_arguments()

    targets.initialize()

    palette = raw_colors.get(args["file"], num_colors=150)

    palette = filters.apply(palette)

    if args["json"]:
        # TODO Saves to Json
        return
    else:
        targets.export(palette, args["file"])
        display_palette(palette)


if __name__ == '__main__':
    main()
