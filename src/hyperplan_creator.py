import cv2
import utils
import numpy as np
import json
from pathlib import Path
import random
import argparse


class HyperplanCreator():
    def __init__(self, out_file):
        self.MIN_HUE        = 0
        self.MAX_HUE        = 359
        self.SIZE_HUE       = 10

        self.MIN_SAT        = 0
        self.MAX_SAT        = 1
        self.SIZE_SAT       = 5

        self.MIN_LUM        = 0
        self.MAX_LUM        = 1
        self.SIZE_LUM       = 10

        self.STEP_SMALL     = 0.01
        self.STEP_LARGE     = 0.1

        self.WIDTH          = 700
        self.HEIGHT         = 800

        self.keys_file      = "keys.json"
        self.hyperplan_file = out_file
        self.keys           = self.__init_keys()


    def __load_keys(self):
        with open(self.keys_file, 'r') as f:
            return json.load(f)


    def __init_keys(self):
        if not Path(self.keys_file).is_file():
            keys = {}
            cv2.namedWindow('Key setter', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('HyperplanCreator', 10, 10)
            for k in ["UP", "DOWN", "RIGHT", "LEFT", "RETURN", "DELETE"]:
                print("Press key: " + str(k))
                keys[k] = cv2.waitKey(0)
            utils.save_json(self.keys_file, keys)
            return keys
        else:
            return self.__load_keys()


    def __display_image(self, image):
        """ Displays a given image """
        cv2.namedWindow('HyperplanCreator', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('HyperplanCreator', self.WIDTH, self.HEIGHT)
        cv2.imshow('HyperplanCreator', image)
        key = cv2.waitKey(0)
        # cv2.destroyAllWindows()
        return key


    def __create_image(self, h, s, l):
        """ Creates an image where on top sits a rectangle of the given color
            and on bottom, lays a text which color is the one provided over a
            black background """
        r, g, b = utils.hsl_to_rgb([h, s, l])
        image = np.zeros((self.HEIGHT, self.WIDTH, 3), np.uint8)
        image[self.HEIGHT//2:] = (0,0,0)
        cv2.putText(image, "Ben deja on", (20, int(self.HEIGHT//4.0)),
                fontFace=0, fontScale=3, lineType=2, thickness=3, color=[b,g,r])
        cv2.putText(image, "aurait une cabane", (20, int(2*self.HEIGHT//4.0)),
                fontFace=0, fontScale=3, lineType=2, thickness=3, color=[b,g,r])
        cv2.putText(image, "Notre Rice a nous", (20, int(3*self.HEIGHT//4.0)),
                fontFace=0, fontScale=3, lineType=2, thickness=3, color=[b,g,r])
        return image


    def __edit_value(self, key, l):
        """ For a given key, increses or decreases the luminosity """
        if key == self.keys["RIGHT"]:
            l += self.STEP_SMALL
        elif key == self.keys["LEFT"]:
            l -= self.STEP_SMALL
        elif key == self.keys["UP"]:
            l += self.STEP_LARGE
        elif key == self.keys["DOWN"]:
            l -= self.STEP_LARGE

        if l < 0: l = 0.0
        elif l > 1: l = 1.0
        return l


    def __refresh_image(self, C, value_to_edit):
        """ For a given hue and saturation, loop for different values of
            luminosity until the user accepts a value """
        image = self.__create_image(C[0], C[1], C[2])
        key = self.__display_image(image)
        if key == self.keys["RETURN"]:
            return -1
        elif key == self.keys["DELETE"]:
            print("The last confirmed color has been removed")
            return -2
        return self.__edit_value(key, value_to_edit)


    def __catesian_product(self, T1, T2):
        product =[]
        for t1 in T1:
            for t2 in T2:
                product.append((t1, t2))
        random.shuffle(product)
        return product


    def luminosity_hyperplan(self):
        saturations = np.linspace(self.MIN_SAT, self.MAX_SAT, self.SIZE_SAT)
        hues = np.linspace(self.MIN_HUE, self.MAX_HUE, self.SIZE_HUE)
        sources = self.__catesian_product(hues, saturations)

        l = 0
        colors = []
        while sources:
            h, s = sources.pop()
            while True:
                res = self.__refresh_image((h, s, l), l)
                if res == -1:
                    colors.append((h, s, l))
                    utils.save_json(self.hyperplan_file, colors)
                    break
                elif res == -2 and colors:
                    tmp_h, tmp_s, _ = colors.pop()
                    sources.append((tmp_h, tmp_s))
                else:
                    l = res
        utils.save_json(self.hyperplan_file, colors)


    def saturation_hyperplan(self):
        luminosities = np.linspace(self.MIN_LUM, self.MAX_LUM, self.SIZE_LUM)
        hues = np.linspace(self.MIN_HUE, self.MAX_HUE, self.SIZE_HUE)
        sources = self.__catesian_product(hues, luminosities)

        s = 0
        colors = []
        while sources:
            h, l = sources.pop()
            while True:
                res = self.__refresh_image((h, s, l), s)
                if res == -1:
                    colors.append((h, s, l))
                    utils.save_json(self.hyperplan_file, colors)
                    break
                elif res == -2 and colors:
                    tmp_h, _, tmp_l = colors.pop()
                    sources.append((tmp_h, tmp_l))
                else:
                    s = res
        utils.save_json(self.hyperplan_file, colors)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--file", help="Path of the output file", required=True)
    ap.add_argument("-t", "--type", help="L for luminosity, S for saturation", required=True)
    args = vars(ap.parse_args())

    hc = HyperplanCreator(args['file'])
    if args['type'] == 'L':
        hc.luminosity_hyperplan()
    elif args['type'] == 'S':
        hc.saturation_hyperplan()
