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
from docopt import docopt
import os

version = 1.0

help_msg = """Hapycolor.

Usage:
  hapycolor (-f [-j] | -d | -x) FILE
  hapycolor [--list-compatible-targets | --list-enabled-targets] ...
  hapycolor [-r | -e | -s] TARGETS ...
  hapycolor -h | --help
  hapycolor --version

Options:
  -h, --help     Show this screen.
  --version      Show version.

  -f, --file     Export image's palette.
  -j, --json     Save image's palette into palettes.json file.
  -x, --export   Export json palette to enabled targets.
  -d, --dir      For each image in the dir, save palette into palettes.json file.

  -r, --reconfigure
                 Reconfigure every target passed in arguments.
  -e, --enable   Enable targets passed in arguments.
                 Argument 'all' enables every compatible targets.
  -s, --disable  Disable targets passed in arguments.
                 Argument 'all' disables every targets.

  --list-enabled-targets
                 List all enabled targets.
  --list-compatible-targets
                 List all compatible targets.
"""

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
    return docopt(help_msg, version=version)


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

    img_path = args['FILE']
    targs = args['TARGETS']

    if args['--list-compatible-targets']:
        tlist = targets.get_compatible_names()
        print("Compatible targets are:")
        for t in tlist:
            print("\t- {}".format(t))

    if args['--list-enabled-targets']:
        tlist = targets.get_enabled()
        print("Enabled targets are:")
        for t in tlist:
            print("\t- {}".format(t.__name__))

    if args['--enable']:
        print(targs)
        if targs == ["all"]:
            targs = targets.get_compatible_names()
        for t in targs:
            if targets.enable(t):
                print("Target {} was already enabled.".format(t))
            else:
                print("Enabled target {}.".format(t))

    if args['--disable']:
        if targs == ["all"]:
            targs = targets.get_compatible_names()
        for t in targs:
            if targets.disable(t):
                print("Target {} was already disabled.".format(t))
            else:
                print("Disabled target {}.".format(t))

    if args['--reconfigure']:
        if targs == []:
            targs = targets.get_compatible_names()
        for t in targs:
            helpers.bold("Reconfiguring target {}".format(t))
            targets.reconfigure(t)
            print()

    if args['--json'] or args['--dir']:
        img_list = []
        if args['--json']:
            img_list.append(img_path)
        elif args['--dir']:
            for f in os.listdir(img_path):
                if os.path.splitext(f)[1] in [".jpg", "jpeg"]:
                    img_list.append(os.path.join(path, f))

        for img in img_list:
            print("Processing file {}".format(img))
            palette = raw_colors.get(img, num_colors=150)
            palette = filters.apply(palette)
            add_palette_json(os.path.abspath(img), palette, "palettes.json")
        print()
        print("Palette saved to palettes.json")
        return

    if args['--file']:
        palette = raw_colors.get(img_path, num_colors=150)
        palette = filters.apply(palette)
    if args['--export']:
        palette = helpers.load_json(img_path)
    if args['--file'] or args['--export']:
        targets.initialize()
        targets.export(palette, img_path)
        display_palette(palette)


if __name__ == '__main__':
    main()
