from ctypes import cdll, c_int, c_char_p, create_string_buffer, pointer
from platform import system

if system() == "Darwin":
    lib = cdll.LoadLibrary("./libcolor_reducer.dylib")
else:
    lib = cdll.LoadLibrary("./libcolor_reducer.so")

colors = [[1,2,3], [10,11,12], [33, 34, 35]]

def decode_colors(string):
    """ Decode a string of colors into a list of triplets """
    colors = []
    i = 0
    while i < len(string):
        colors.append([ord(string[i]),
                       ord(string[i + 1]),
                       ord(string[i + 2])])
        i = i + 3
    return colors

def encode_colors(colors):
    """ Encode a list of colors defined by triplets into a string """
    values = []
    for i, c in enumerate(colors):
        values.extend([chr(c[0]), chr(c[1]), chr(c[2])])
    return "".join(values)

print colors

in_string = c_char_p(encode_colors(colors))
out_string = c_char_p("a" * (len(colors) * 3 + 1))

lib.reduce_colors(in_string, out_string)

print decode_colors(out_string.value)

