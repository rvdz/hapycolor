import visual
import utils
import color_extractor
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

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--file", help="File path to the image", required=False)
    args = vars(ap.parse_args())

    extractor = color_extractor.ColorExtractor(args["file"], num_colors=250)
    colors = extractor.get_colors()
    fg = colors["special"]["foreground"]
    bg = colors["special"]["background"]
    others = colors["colors"]

    rgbcols = [utils.hex_to_rgb(others[k]) for k in others]

    print("\nFinal palette (" + str(len(rgbcols)) + "):")
    visual.print_palette(rgbcols, size=2)

    print("\Foreground color:")
    visual.print_palette([utils.hex_to_rgb(fg)], size=4)

    print("\Background color:")
    visual.print_palette([utils.hex_to_rgb(bg)], size=4)

    colors_to_file([others[k] for k in others], "palette.png")
    utils.save_json("palette.json", colors)
