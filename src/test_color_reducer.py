from time import sleep, time
from random import randint, shuffle, random
from termcolor import colored
import matplotlib.pyplot  as plt


THRESHOLD = 50

def show_statistics(durations, lengths):
    plt.plot(lengths, durations, 'ro')
    plt.show()

def algorithm(colors):
    start_time = time()
    # Do magic
    sleep(random())
    time_elapsed = time() - start_time
    return colors, time_elapsed

def generate_optimal_result(length):
    colors = [0]
    for i in range(length - 1):
        colors.append(colors[-1] + THRESHOLD)
    return colors

def add_noise(colors, length):
    min_val = colors[0]
    max_val = colors[-1]

    for i in range(length):
        colors.append(randint(min_val, max_val))

def test_algorithm(res_length, noise_length):
    colors = generate_optimal_result(res_length)
    expected_result = colors[:]
    add_noise(colors, noise_length)
    shuffle(colors)
    result, duration = algorithm(colors)
    result.sort()
    err = 0
    for i in range(len(result)):
        if i < len(expected_result) and result[i] != expected_result[i]:
            err += 1
    if err != 0:
        print colored("Input length: " + str(len(colors)) + "\t| Expected result: " + str(len(expected_result)) + "\t| Result: " + str(len(result)), "red")
    else:
        print colored("Correct result over " + str(len(colors)) + " entries", "green")
    return duration, len(colors)

NUM_TESTS = 40
durations = []
lengths = []
for i in range(NUM_TESTS):
    res = test_algorithm(randint(0, 50), randint(0, 100))
    durations.append(res[0])
    lengths.append(res[1])
show_statistics(durations, lengths)


