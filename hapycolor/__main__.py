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
  hapycolor --reconfigure TARGETS ...
  hapycolor --print-config TARGETS ...
  hapycolor [-e EN_TARGETS ... | -s DIS_TARGETS ...] ...
  hapycolor -l | --list-all
  hapycolor [--list-compatible-targets | --list-enabled-targets | --list-all-targets] ...
  hapycolor -h | --help
  hapycolor --version

Options:
  -h, --help     Show this screen.
  --version      Show version.

  -f, --file     Export image's palette.
  -j, --json     Save image's palette into palettes.json file.
  -x, --export   Export json palette to enabled targets.
  -d, --dir      For each image in the dir, saves palette into palettes.json file.

  -r, --reconfigure
                 Reconfigure every target passed in arguments.
                 (Separated by spaces)
  -p, --print-config
                 Print configuration of targets passed in arguments.
                 Argument 'all' prints the whole config.

  -e, --enable   Enable targets passed in arguments.
                 Argument 'all' enables every compatible targets.
  -s, --disable  Disable targets passed in arguments.
                 Argument 'all' disables every targets.

  -l, --list-all
                 Triggers all following listing options.
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
    targs = args['TARGETS'] if args['TARGETS'] else args['EN_TARGETS']
    distargs = args['DIS_TARGETS']
    if targs == ["all"]:
        targs = targets.get_compatible_names()
    if distargs == ["all"]:
        distargs = targets.get_compatible_names()
    # Capitalize first letter for esthetics and access
    targs = [t[0].upper() + t[1:] for t in sorted(targs)]
    distargs = [t[0].upper() + t[1:] for t in sorted(distargs)]

    if args['--list-all']:
        args['--list-all-targets'] = True
        args['--list-compatible-targets'] = True
        args['--list-enabled-targets'] = True

    if args['--list-all-targets']:
        tlist = targets.get_all_names()
        helpers.bold("Targets are:")
        for t in tlist:
            print("    - {}".format(t))

    if args['--list-compatible-targets']:
        tlist = targets.get_compatible_names()
        if not tlist:
            helpers.bold("No compatible targets.")
        else:
            helpers.bold("Compatible targets are:")
            for t in tlist:
                print("    - {}".format(t))

    if args['--list-enabled-targets']:
        tlist = targets.get_enabled()
        if not tlist:
            helpers.bold("No enabled targets.")
        else:
            helpers.bold("Enabled targets are:")
            for t in tlist:
                print("    - {}".format(t.__name__))

    if args['--enable']:
        for t in targs:
            if targets.enable(t):
                print("Target {} was already enabled.".format(t))
            else:
                print("Enabled target {}.".format(t))

    if args['--disable']:
        for t in distargs:
            if targets.disable(t):
                print("Target {} was already disabled.".format(t))
            else:
                print("Disabled target {}.".format(t))

    if args['--print-config']:
        for t in targs:
            helpers.bold("Configuration of target {}:".format(t))
            cfg = config.load(t)
            print("    enabled: {}".format(cfg["enabled"]))
            for key in (k for k in cfg if k != "enabled"):
                print("    {}: {}".format(key, cfg[key]))

    if args['--reconfigure']:
        for t in targs:
            helpers.bold("Reconfiguring target {}".format(t))
            targets.reconfigure(t)

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
