import cv2
from utils import hsl_to_rgb
from utils import hsl_to_hex
import sys
import colorsys
import numpy as np
import json

# The output file
if len(sys.argv) != 2:
    print "Usage: hyperplan_creator.py <output_file_name>"
    exit()

data_file = sys.argv[1]

MIN_HUE = 0
MAX_HUE = 360
SIZE_H = 10

MIN_SAT = 0
MAX_SAT = 1
SIZE_S = 10

STEP_L_SMALL  = 0.01
STEP_L_LARGEL = 0.1

WIDTH   = 700
HEIGHT  = 800

RETURN  = 13
UP      = 0
DOWN    = 1
LEFT    = 2
RIGHT   = 3
DELETE = 127

hues        = np.linspace(MIN_HUE, MAX_HUE, SIZE_H)
saturations = np.linspace(MIN_SAT, MAX_SAT, SIZE_S)

# Displays a given image
def display_image(image):
    cv2.namedWindow('HyperplanCreator', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('HyperplanCreator', WIDTH, HEIGHT)
    cv2.imshow('HyperplanCreator', image)
    key = cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return key

# Creates an image where on top sits a rectangle of the given color and on
# bottom, lays a text which color is the one provided over a black background
def create_image(h, s, l):
    r, g, b = hsl_to_rgb([h, s, l])
    image = np.zeros((HEIGHT,WIDTH,3), np.uint8)
    image[0:HEIGHT/2] = (b, g, r)
    image[HEIGHT/2:] = (0,0,0)
    cv2.putText(
            image,
            "Notre Rice a nous",
            (20, int(3*HEIGHT/4.0)),
            cv2.FONT_HERSHEY_TRIPLEX,
            2,
            [b,g,r])
    return image

# For a given key, increses or decreases the luminosity
def edit_luminosity(key, l):
    if key == RIGHT:
        l += STEP_L_SMALL
    elif key == LEFT:
        l -= STEP_L_SMALL
    elif key == UP:
        l += STEP_L_LARGEL
    elif key == DOWN:
        l -= STEP_L_LARGEL

    if l < 0:
        l = 0.0
    elif l > 1:
        l = 1.0
    return l

def save_json(array):
    with open(data_file, 'w') as f:
        json.dump(array, f, indent=4)

l = 0
h = 100
s = 0
values = []
removed = []

def choose_luminosity(h, s, l):
    while True:
        image = create_image(h, s, l)
        key = display_image(image)
        print "Current luminosity: " + str(l)
        if key == RETURN:
            values.append([h, s, l])
            break
        elif key == DELETE:
            if values:
                print "The last color has been removed"
                removed.append(values.pop())
        l = edit_luminosity(key, l)
    return l

for h in hues:
    for s in saturations:
        l = choose_luminosity(h, s, l)

while removed:
    color = removed.pop()
    choose_luminosity(color[0], color[1], color[2])


save_json(values)

