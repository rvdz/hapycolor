## -*- coding: UTF-8 -*-
""" Utilitary methods to display ouputs """

# Add color to a string
def str_color(message, rgbcol):
    r,g,b = rgbcol
    return "\033[38;2;{};{};{}m{}\033[0m".format(r,g,b,message)

# print(squares from a palette)
def print_palette(rgbcols, size=2):
    str_palette = ""
    for col in rgbcols:
        str_palette += str_color("██"*size, col)
    # for s in range(size):
    print(str_palette)


