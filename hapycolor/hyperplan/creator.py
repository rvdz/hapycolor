from .color import refine
from . import config
from . import helpers

from enum import IntEnum
from math import sqrt, cos, sin
import argparse
import cv2
import numpy as np
import pathlib
import random

class HyperplanCreator():
    def __init__(self, filter_type, is_calibrating):
        # Values: "bright", "dark", "saturation"
        self.filter_type        = filter_type
        self.is_calibrating     = is_calibrating
        self.calibration_points = 10

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

        self.hyperplan_file = config.Config.get_hyperplan_file(filter_type)
        self.Key            = self.__init_keys()

    def run(self):
        if not self.is_calibrating and (self.filter_type == config.FilterEnum.DARK or \
                                        self.filter_type == config.FilterEnum.BRIGHT):
            hc.luminosity_hyperplan()

        elif not self.is_calibrating and self.filter_type == config.FilterEnum.SATURATION:
            hc.saturation_hyperplan()

        elif self.is_calibrating and (self.filter_type == config.FilterEnum.DARK or \
                                      self.filter_type == config.FilterEnum.BRIGHT):
            hc.calibrate_luminosity_hyperplan()

    def __init_keys(self):
        """ Returns an enumeration called 'Key', that matches each key to its openCV's value """
        keys = {}
        if not pathlib.Path(config.get_keys().is_file()):
            cv2.namedWindow('Key setter', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('HyperplanCreator', 10, 10)
            for k in ["UP", "DOWN", "RIGHT", "LEFT", "RETURN", "DELETE"]:
                print("Press key: " + str(k))
                keys[k] = cv2.waitKey(0)
            helpers.save_json(config.get_keys(), keys)
        else:
            keys = helpers.load_json(config.get_keys())
        return IntEnum("Key", [(k, keys[k]) for k in keys])


    def __display_image(self, image):
        """ Displays a given image """
        cv2.namedWindow('HyperplanCreator', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('HyperplanCreator', self.WIDTH, self.HEIGHT)
        cv2.imshow('HyperplanCreator', image)
        key = cv2.waitKey(0)
        # cv2.destroyAllWindows()
        return key


    def __add_frame(self, image, color):
        green = (0, 255, 0)
        red   = (0, 0, 255)

        if self.filter_type == config.FilterEnum.BRIGHT:
            fill_color = red if self.cf.is_too_bright(color) else green
        elif self.filter_type == config.FilterEnum.DARK:
            fill_color = red if self.cf.is_too_dark(color) else green
        cv2.rectangle(image, (0, 0), (self.WIDTH, self.HEIGHT), fill_color, 5)
        return image


    def __create_image(self, hsl_color):
        """ Creates an image where on top sits a rectangle of the given color
            and on bottom, lays a text which color is the one provided over a
            black background """
        r, g, b = helpers.hsl_to_rgb(hsl_color)
        image = np.zeros((self.HEIGHT, self.WIDTH, 3), np.uint8)
        image[self.HEIGHT//2:] = (0,0,0)
        cv2.putText(image, "Ben deja on", (20, int(self.HEIGHT//4.0)),
                fontFace=0, fontScale=3, lineType=2, thickness=3, color=[b,g,r])
        cv2.putText(image, "aurait une cabane", (20, int(2*self.HEIGHT//4.0)),
                fontFace=0, fontScale=3, lineType=2, thickness=3, color=[b,g,r])
        cv2.putText(image, "Notre Rice a nous", (20, int(3*self.HEIGHT//4.0)),
                fontFace=0, fontScale=3, lineType=2, thickness=3, color=[b,g,r])

        if self.is_calibrating:
            return self.__add_frame(image, hsl_color)
        return image


    def __edit_value(self, key, l):
        """ For a given key, increses or decreases the luminosity """
        if key == self.Key.RIGHT:
            l += self.STEP_SMALL
        elif key == self.Key.LEFT:
            l -= self.STEP_SMALL
        elif key == self.Key.UP:
            l += self.STEP_LARGE
        elif key == self.Key.DOWN:
            l -= self.STEP_LARGE

        if l < 0: l = 0.0
        elif l > 1: l = 1.0
        return l


    def __refresh_image(self, C, value_to_edit):
        """ For a given hue and saturation, loop for different values of
            luminosity until the user accepts a value """
        image = self.__create_image(C)
        key = self.__display_image(image)
        if key == self.Key.RETURN:
            return -1
        elif key == self.Key.DELETE:
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


    def calibrate_luminosity_hyperplan(self):
        print("Calibrating luminosity")
        self.cf = refine.Refine()
        colors = []
        for i in range(self.calibration_points):
            colors.append((random.randint(0, 360), random.random(), random.random()))

        while colors:
            h, s, l = colors.pop()
            while True:
                res = self.__refresh_image((h, s, l), l)
                if res == -1:
                    self.__update_json((h, s, l))
                    break
                else:
                    l = res


    def __update_json(self, color):
        """ Finds nearest point to 'color' and update its luminosity """
        colors = helpers.load_json(self.hyperplan_file)
        distances = {}
        for c in colors:
            distances[tuple(c)] = self.__distance(c[:2], color[:2])

        old_color = min(distances, key=distances.get)
        del distances[old_color]

        new_colors = list(distances)
        new_colors.append((old_color[0], old_color[1], c[2]))
        # TODO: In debug phase, do not alter the hyperplan file
        helpers.save_json(self.hyperplan_file, new_colors)


    def __distance(self, P1, P2):
        """ Distance between two points in cylidrical coordinates """
        r1, t1 = P1
        r2, t2 = P2
        return sqrt(r1**2 + r2**2 - 2*r1*r2*(cos(t1)*cos(t2) - sin(t1)*sin(t2)))

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
                    helpers.save_json(self.hyperplan_file, colors)
                    break
                elif res == -2 and colors:
                    tmp_h, tmp_s, _ = colors.pop()
                    sources.append((tmp_h, tmp_s))
                else:
                    l = res
        helpers.save_json(self.hyperplan_file, colors)


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
                    helpers.save_json(self.hyperplan_file, colors)
                    break
                elif res == -2 and colors:
                    tmp_h, _, tmp_l = colors.pop()
                    sources.append((tmp_h, tmp_l))
                else:
                    s = res
        helpers.save_json(self.hyperplan_file, colors)


def filter_type(t):
    if t == "bright":
        return config.FilterEnum.BRIGHT
    elif t == "dark":
        return config.FilterEnum.DARK
    elif t == "saturation":
        return config.FilterEnum.SATURATION
    else:
        raise argparse.ArgumentTypeError("Filter type must be 'dark'|'bright'|'saturation'")


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-t", "--type", help="Filter type: 'dark'|'bright'|'saturation'", type=filter_type, \
                    required=True)
    ap.add_argument("-c", "--calibrate", help="Calibrate an existing hyperplan", \
                    required=False, action="store_true")

    args = vars(ap.parse_args())
    hc = HyperplanCreator(args['type'], args['calibrate'])
    hc.run()
