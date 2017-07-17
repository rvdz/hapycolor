from color_extractor import ColorExtractor
from PIL import Image, ImageDraw
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
    extractor = ColorExtractor(sys.argv[1], num_colors=200)
    colors = extractor.get_colors()
    for col in colors:
        print(col)
    colors_to_file(colors, "palette.png")
