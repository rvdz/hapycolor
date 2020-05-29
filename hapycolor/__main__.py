"""

888   |                              e88~-_           888
888___|   /~~~8e  888-~88e  Y88b  / d888   \  e88~-_  888  e88~-_  888-~_
888   |       88b 888  888b  Y888/  8888     d888   i 888 d888   i 888
888   |  e88~-888 888  8888   Y8/   8888     8888   | 888 8888   | 888
888   | C888  888 888  888P    Y    Y888   / Y888   | 888 Y888   | 888
888   |  \88_-888 888-_88/    /      \88_-~   \88_-~  888  \88_-~  888
                  888       _/

"""

from hapycolor import config, visual, helpers, targets, raw_colors, filters, imgur
from hapycolor import exceptions
from hapycolor import palette as pltte

from PIL import Image, ImageDraw
from docopt import docopt
import os
import pathlib
from hapycolor.__version__ import __version__


help_msg = """Hapycolor.

Usage:
  hapycolor (--imgur URL | -f FILE) [(--json | --Xresources | --rasi) ... -o OUTPUT_DIR]
  hapycolor --export-from-json FILE
  hapycolor --dir DIRECTORY (--json | --Xresources | --rasi) ... -o OUTPUT_DIR
  hapycolor --reconfigure TARGETS ...
  hapycolor --print-config TARGETS ...
  hapycolor [-e EN_TARGETS ... | -d DIS_TARGETS ...] ...
  hapycolor -l | --list-all
  hapycolor [--list-compatible-targets | --list-enabled-targets | --list-all-targets] ...
  hapycolor -h | --help
  hapycolor --version

Options:
  -h, --help     Show this screen.
  --version      Show version.

  -f, --file     The path of the source image from which the palette will be generated.
  --dir          Generates a palette for each image in the provided directory, without exporting them.
  -o, --output   Target directory where the palettes will be saved.
  --imgur        The url of an image from imgur.com from which the palette will be generated.
  --json         Save image's palette into the provided directory, without exporting it.
  --Xresources   Save palette as Xresources format in OUTPUT_DIR, without exporting it..
  --rasi         Save palette as rasi format in OUTPUT_DIR, without exporting it.
  --export-from-json
                 Export json palette to enabled targets.

  -r, --reconfigure
                 Reconfigure every target passed in arguments.
                 (Separated by spaces)
  -p, --print-config
                 Print configuration of targets passed in arguments.
                 Argument 'all' prints the whole config.

  -e, --enable   Enable targets passed in arguments.
                 Argument 'all' enables every compatible targets.
  -d, --disable  Disable targets passed in arguments.
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
    return docopt(help_msg, version="Hapycolor " + str(__version__))



def display_palette(palette):
    print("\nFinal palette (" + str(len(palette.colors)) + "):")
    visual.print_palette(palette.colors, size=2)

    print("\nForeground color:")
    visual.print_palette([palette.foreground], size=4)

    print("\nBackground color:")
    visual.print_palette([palette.background], size=4)

    # colors_to_file([c for c in palette.colors], "palette.png")
    # palette.to_json("palette.json")


def add_palette_json(img_name, palette, filename):
    hexcolors = palette.hexcolors()
    data_dict = {foreground: hexcolors[0],
                 background: hexcolors[1],
                 colors: hexcolors[2]}
    helpers.update_json(filename, data_dict)


def main(args=None):

    config.create_config()
    args = parse_arguments()

    targs = args['TARGETS'] if args['TARGETS'] else args['EN_TARGETS']
    distargs = args['DIS_TARGETS']
    if targs == ["all"]:
        targs = targets.get_compatible_names()
    if distargs == ["all"]:
        distargs = targets.get_compatible_names()

    # Resolve targets
    try:
        targs = [targets.get_class(t) for t in targs]
        distargs = [targets.get_class(t) for t in distargs]
    except exceptions.InvalidTarget as exc:
        print(exc)
        return

    if args['--list-all']:
        args['--list-all-targets'] = True
        args['--list-compatible-targets'] = True
        args['--list-enabled-targets'] = True

    if args['--list-all-targets']:
        tlist = targets.get_all_names()
        helpers.bold("Targets are:")
        for t in tlist:
            print("\t- {}".format(t))

    if args['--list-compatible-targets']:
        tlist = targets.get_compatible_names()
        if not tlist:
            helpers.bold("No compatible targets.")
        else:
            helpers.bold("Compatible targets are:")
            for t in tlist:
                print("\t- {}".format(t))

    if args['--list-enabled-targets']:
        tlist = targets.get_enabled()
        if not tlist:
            helpers.bold("No enabled targets.")
        else:
            helpers.bold("Enabled targets are:")
            for t in tlist:
                print("\t- {}".format(t.__name__))

    if args['--enable']:
        for t in targs:
            if not t.is_config_initialized():
                targets.initialize_target(t)
            if t.is_enabled():
                print("Target {} was already enabled.".format(t.__name__))
            else:
                t.enable()
                print("Enabled target {}.".format(t.__name__))

    if args['--disable']:
        for t in distargs:
            if not t.is_enabled():
                print("Target {} was already disabled.".format(t.__name__))
            else:
                t.disable()
                print("Disabled target {}.".format(t.__name__))

    if args['--print-config']:
        for t in targs:
            helpers.bold("Configuration of target {}:".format(t.__name__))
            if not t.is_config_initialized():
                print("\tTarget has not been initialized.")
                continue
            try:
                cfg = t.load_config()
                for key in cfg:
                    print("\t{}: {}".format(key, cfg[key]))
            except exceptions.InvalidConfigKeyError:
                pass

    if args['--reconfigure']:
        for t in targs:
            helpers.bold("Reconfiguring target {}".format(t.__name__))
            targets.reconfigure(t)

    try:
        max_colors = 160
        img_list = []

        # Checking provided files and directories
        if args['--export-from-json'] or args['--file']:
            if not pathlib.Path(args['FILE']).resolve().exists():
                msg = "ERROR: The provided image does not exist"
                raise exceptions.ImageNotFoundException(msg)
            img_list.append(args['FILE'])

        if args['--json'] or args['--dir']:
            if not pathlib.Path(args['OUTPUT_DIR']).exists():
                msg = "ERROR: The provided output directory does not exist"
                raise exceptions.InvalidDirectoryException(msg)
            if args['--dir']:
                for f in os.listdir(args['DIRECTORY']):
                    if os.path.splitext(f)[1] in [".jpg", ".jpeg", ".png"]:
                        img_list.append(os.path.join(args['DIRECTORY'], f))

        # Extracting palettes
        palettes = []
        if args['--imgur']:
            local_path = imgur.download(args['URL'])
            print("Processing file {}".format(local_path))
            palettes.append(raw_colors.get(local_path,
                                           num_colors=max_colors))
            palettes[-1] = filters.apply(palettes[-1])
            img_list.append(local_path)
        if args['--file'] or args['--dir']:
            for img in img_list:
                print("Processing file {}".format(img))
                palettes.append(raw_colors.get(img, num_colors=max_colors))
                palettes[-1] = filters.apply(palettes[-1])
        if args['--export-from-json']:
            palettes.append(pltte.Palette.from_json(img_list[0]))

        # Saving palettes in a json file
        if args['--json'] or args['--dir'] or args['--Xresources'] or args['--rasi']:
            output_dir = pathlib.Path(args['OUTPUT_DIR']).expanduser()
            get_path = lambda i, ext: helpers.get_output_path(output_dir, img_list[i], ext)
            for i, _ in enumerate(img_list):
                if args['--json']:
                    palettes[i].to_json(get_path(i, '.json'))
                if args['--Xresources']:
                    palettes[i].to_Xresources(get_path(i, '.Xresources'))
                if args['--rasi']:
                    palettes[i].to_rasi(get_path(i, '.rasi'))

        # Exporting the first palette
        elif args['--imgur'] or args['--file'] or args['--export-from-json']:
            targets.export(palettes[0], img_list[0])
            display_palette(palettes[0])
    except exceptions.ImageNotFoundException as inf:
        print(inf.msg)
    except exceptions.InvalidDirectoryException as ide:
        print(ide.msg)
    except exceptions.PaletteFormatError as pfe:
        print(pfe.msg)
    except exceptions.InvalidImageException as iie:
        print(iie.msg)


if __name__ == '__main__':
    main()
