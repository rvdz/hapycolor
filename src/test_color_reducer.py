from random import randint
from time import sleep, time
from platform import system
import matplotlib.pyplot  as plt
from ctypes import cdll, c_void_p, c_uint, c_char_p, create_string_buffer, pointer, byref

log_file = "log.txt"
THRESHOLD = 30000

if system() == "Darwin":
    lib = cdll.LoadLibrary("./libcolor_reducer.dylib")
else:
    lib = cdll.LoadLibrary("./libcolor_reducer.so")

def decode_colors_id(string, input_colors):
    """ Decode a string where an integer is encoded over four bytes. The even ones
        contain either '\x01' or '\x02' if the following value is null. The odd
        ones contain a dummy value if it should be null, or the actual value """
    colors = []
    i = 0
    while i < len(string):
        index = 0
        if string[i] == '\x02':
            index = ord(string[i + 1]) * 256
        if string[i + 2] == '\x02':
            index += ord(string[i + 3]);
        colors.append(input_colors[index])
        i += 4
    return colors

def encode_colors_id(graph):
    """ Encode a string where an integer is encoded over four bytes. The even ones
        contain either '\x01' if the following value is null or '\x02'. The odd
        ones contain a dummy value if it should be null, or the actual value """
    string = []
    for c in graph:
        if c / 256 == '\x00':
            string.append('\x01')
            string.append('\x01')
        else:
            string.append('\x02')
            string.append(chr(c / 256))

        if c % 256 == 0:
            string.append('\x01')
            string.append('\x01')
        else:
            string.append('\x02')
            string.append(chr(c % 256))
    return "".join(string)

def distance(c1, c2):
    return pow(c1[0] - c2[0], 2) + pow(c1[1] - c2[1], 2) + pow(c1[2] - c2[2], 2)

def color_reducer(colors):
    # Generate a graph where the vertices that are far enough own a common edge
    graph = []
    for i1, c1 in enumerate(colors):
        for i2, c2 in enumerate(colors):
            if c1 != c2 and distance(c1, c2) > THRESHOLD:
                graph.extend([i1, i2])

    in_string = c_char_p(encode_colors_id(graph))
    out_string = c_char_p('\x00' * (len(colors) * 4 + 1))

    number_color_in = c_uint(len(graph) / 2)
    start_time = time()
    lib.color_reducer(in_string, number_color_in, out_string)
    time_elapsed = time() - start_time

    result = decode_colors_id(out_string.value, colors)

    return result, time_elapsed

def check_result(colors):
    for c1 in colors:
        for c2 in colors:
            if c1 != c2 and distance(c1, c2) < THRESHOLD:
                print "Wrong result"
                return False;
    print "Correct result"
    return True

def show_statistics(lengths, durations):
    plt.plot(lengths, durations, 'ro')
    plt.show()

durations = []
lengths = []
for t in range(20):
    colors = []
    for i in range(randint(50, 1000)):
        colors.append((randint(0, 255), randint(0, 255), randint(0, 255)))
    colors = list(set(colors))
    res, duration = color_reducer(colors)
    durations.append(duration)
    lengths.append(len(colors))
    check_result(res)

show_statistics(lengths, durations)
