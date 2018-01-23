from PIL import Image
import argparse
import json
import os

def resize_image(img, maxsize=500):
    width, height = img.size
    if min(height, width) > maxsize:
        if width > height:
            f = float(maxsize) / width
            img = img.resize((maxsize, int(height*f)), Image.ANTIALIAS)
        else:
            f = float(maxsize) / height
            img = img.resize((int(width*f), maxsize), Image.ANTIALIAS)
    return img

def get_palette_dim(img_width, palette, maxsize=40):
    palette_dim = min(int(img_width / len(palette)), maxsize)
    return palette_dim


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--file", help="File path to the json. "
            + "(Json format must be: {\"path\": \"palette\"})", required=True)
    ap.add_argument("-d", "--dir", help="Directory where to save the images "
            + "generated")
    args = vars(ap.parse_args())

    json_file = args["file"]

    with open(json_file) as f:
        data = json.load(f)

    for img_path, palette in data.items():
        img = Image.open(img_path)
        img = resize_image(img, maxsize=600)
        dim = img.size
        palette_dim = get_palette_dim(dim[0], palette)
        new_img = Image.new("RGB", (dim[0], dim[1]+palette_dim))
        new_img.paste(img, (0,0))

        pixels = new_img.load()
        for n, col in enumerate(palette):
            for i in range(n*palette_dim, (n+1)*palette_dim):
                for j in range(palette_dim):
                    pixels[i,dim[1]+j] = tuple(col)

        if args["dir"]:
            new_img_name = "palette_{}".format(os.path.basename(img_path))
            save_path = os.path.join(args["dir"], new_img_name)
            new_img.save(save_path)
        else:
            new_img.show()

if __name__ == '__main__':
    main()
