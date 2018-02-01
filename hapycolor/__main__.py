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
from . import exceptions

from PIL import Image, ImageDraw
import argparse
import os


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
    ap.add_argument("-d", "--dir", help="Directory path to the images "
                    + "(this option will NOT export variables, use -f instead)"
                    + ". This option implicitly enables -j option")
    ap.add_argument("-j", "--json", action="store_true", help="Saves output "
              + "(RGB format) in a Json file palettes.json instead of "
              + "exporting variables. Json file is updated if the file exists.")
    ap.add_argument("-lct", "--list-compatible-targets", action="store_true", help="List all compatible targets.")
    ap.add_argument("-let", "--list-enabled-targets", action="store_true", help="List all enabled targets.")
    ap.add_argument("-r", "--reconfigure", metavar="target", nargs="*", type=str, help="Reconfigure all targets passed in arguments.")
    ap.add_argument("-en", "--enable", metavar="target", nargs="+", type=str, help="Enable targets passed in arguments. To enable every targets compatible, argument can be 'all'.")
    ap.add_argument("-dis", "--disable", metavar="target", nargs="+", type=str, help="Disable targets passed in arguments. To disable every targets, argument can be 'all'.")
    args = vars(ap.parse_args())
    #if not (args["file"] or args["dir"]):
    #    ap.error('expected either argument -f or -d')
    if args["file"] and args["dir"]:
        ap.error('cannot use simultaneaously option -f and -d')
    return args


def display_palette(palette):
    print("\nFinal palette (" + str(len(palette.colors)) + "):")
    visual.print_palette(palette.colors, size=2)

    print("\nForeground color:")
    visual.print_palette([palette.foreground], size=4)

    print("\nBackground color:")
    visual.print_palette([palette.background], size=4)

    colors_to_file([c for c in palette.colors], "palette.png")
    helpers.save_json("palette.json", palette.colors)


def add_palette_json(img_name, palette, filename):
    data_dict = {img_name: palette.hexcolors}
    helpers.update_json(filename, data_dict)


def main(args=None):

    config.create_config()
    args = parse_arguments()

    img_name = args["file"]
    img_dir = args["dir"]

    if args["list_compatible_targets"] \
            or args["list_enabled_targets"]:
        if args["list_compatible_targets"]:
            tlist = targets.get_compatible_names()
            print("Compatible targets are:")
            for t in tlist:
                print("\t- {}".format(t))

        if args["list_enabled_targets"]:
            tlist = targets.get_enabled()
            print("Enabled targets are:")
            for t in tlist:
                print("\t- {}".format(t.__name__))
        return

    if args["json"] or args["dir"]:
        img_list = []
        if img_name is not None:
            img_list.append(img_name)
        elif img_dir is not None:
            for f in os.listdir(img_dir):
                if os.path.splitext(f)[1] in [".jpg", "jpeg"]:
                    img_list.append(os.path.join(img_dir, f))

        for img in img_list:
            print("Processing file {}".format(img))
            try:
                palette = raw_colors.get(img, num_colors=200)
            except exceptions.InvalidImageException as e:
                print(e)
                return
            palette = filters.apply(palette)
            add_palette_json(os.path.abspath(img), palette, "palettes.json")
        print()
        print("Palette saved to palettes.json")

    elif args["reconfigure"] is not None:
        tlist = args["reconfigure"]
        if tlist == []:
            tlist = targets.get_compatible_names()
        for t in tlist:
            helpers.bold("Reconfiguring target {}".format(t))
            targets.reconfigure(t)
            print()

    elif args["enable"] is not None:
        tlist = args["enable"]
        if tlist == ["all"]:
            tlist = targets.get_compatible_names()
        for t in tlist:
            if targets.enable(t):
                print("Target {} was already enabled.".format(t))
            else:
                print("Enabled target {}.".format(t))
    elif args["disable"] is not None:
        tlist = args["disable"]
        if tlist == ["all"]:
            tlist = targets.get_compatible_names()
        for t in tlist:
            if targets.disable(t):
                print("Target {} was already disabled.".format(t))
            else:
                print("Disabled target {}.".format(t))

    else:
        try:
            palette = raw_colors.get(img_name, num_colors=200)
        except exceptions.InvalidImageException as e:
            print(e)
            return
        visual.print_palette(palette.colors, size=2)
        palette = filters.apply(palette)
        targets.initialize()
        targets.export(palette, args["file"])
        display_palette(palette)


if __name__ == '__main__':
    main()
