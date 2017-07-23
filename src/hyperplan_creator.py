import cv2
import colorsys
import numpy as np

MIN_HUE = 0
MAX_HUE = 360
SIZE_H = 10

MIN_SAT = 0
MAX_SAT = 1
SIZE_S = 10

STEP_L = 0.1

WIDTH  = 200
HEIGHT = 200

RETURN = 13
RIGHT = 3
LEFT = 2

hues = np.linspace(MIN_HUE, MAX_HUE, SIZE_H)
saturations = np.linspace(MIN_SAT, MAX_SAT, SIZE_S)

def display_image(image):
    cv2.namedWindow('dst_rt', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('dst_rt', WIDTH, HEIGHT)
    cv2.imshow('dst_rt', image)
    key = cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return key



def create_image(h, s, l):
    r, g, b = colorsys.hls_to_rgb(h, s, l)
    bgr_image = np.zeros((HEIGHT,WIDTH,3), np.uint8)
    bgr_image[:] = (b, g, r)
    return bgr_image


l = 0
h = 100
s = 0.5
for h in hues:
    for s in saturations:
        while True:
            print "Luminosity: " + str(l)
            image = create_image(h, s, l)
            key = display_image(image)
            if key == RETURN:
                break
            elif key == RIGHT:
                l += STEP_L
            elif key == LEFT:
                l -= STEP_L


