from scipy.interpolate import griddata
from  matplotlib import pyplot as plt
from utils import hsl_to_rgb
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import json
from sys import argv, maxint

if len(argv) != 2:
    print "Usage: interpolate_surface.py <file_name.json>"
    exit()

def polar_to_cartesian(data):
    """ Converts a point defined in a polar base in a cartesian base """
    points = []
    values = []
    for e in data:
        points.append(
                [e[1] * np.cos(np.radians(e[0])),
                 e[1] * np.sin(np.radians(e[0])) ] )
        values.append(e[2])
    return np.asarray(points), np.asarray(values)

def convert_to_cartesian(color):
    return color[1] * np.cos(np.radians(color[0])), color[1] * np.sin(np.radians(color[0])), color[2]

def load_points(file_path):
    """ Load hsl points stored in a json file """
    with open(file_path) as f:
        data = json.load(f)
    return data

def display_interpolation(X, Y, Z):
    """ Displays the wireframe of a surface """
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_wireframe(X, Y, Z) #, cmap=plt.cm.YlGnBu_r)
    plt.show()

def display_surface(X, Y, Z, colors):
    """ Displays a scatter plot where each color is represented by a
    a color of the given list """
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(X, Y, Z, c=colors)
    plt.show()

def find_interval(value, X):
    i = 0
    while X[i] < value:
        i += 1
    return i

def find_nearest(P, X, Y, Z):
    """ Returns the luminosity of the nearest interpolated point of
        the given point P """
    real_points = []
    for i in range(len(X)):
        # Search nearest point of the upper portion of the circle
        j = 0
        while Z[i, j] !=  Z[i, j]:
            # If there are no values along this axis
            j += 1
            if j + 1 > len(Y):
                break

        if j + 1 > len(Y):
            continue
        real_points.append([i, j])
        # Search nearest point of the lower portion of the circle
        j = len(Y) - 1
        while Z[i, j] != Z[i, j]:
            j -= 1
        real_points.append([i, j])

    distance = maxint
    nearest_point = []
    for p in real_points:
        if get_distance(P, p) < distance:
            distance = get_distance(P, p)
            nearest_point = p
    return Z[nearest_point[0], nearest_point[1]]

def get_distance(p1, p2):
    return pow(p1[0] - p2[0], 2) + pow(p1[1] - p2[1], 2)

def is_dark(hsl_color, X, Y, Z):
    """ Returns a boolean depending if the given color is too dark.
        The color provided must be in hsl format"""
    color = convert_to_cartesian(hsl_color)
    step_x = X[1] - X[0]
    step_y = Y[1] - Y[0]
    index_x = find_interval(color[0], X)
    index_y = find_interval(color[1], Y)
    if Z[index_x, index_y] != Z[index_x, index_y]:
        Z[index_x, index_y] = find_nearest([color[0], color[1]], X, Y, Z)
    if color[2] < Z[index_x, index_y]:
        return True
    return False

# Set up grid
grid_x, grid_y = np.mgrid[-1:1:100j, -1:1:100j]
axis_x = [x[0] for x in grid_x]
axis_y = grid_y[0]

# Load the provided points
data = load_points(argv[1])
points, values = polar_to_cartesian(data)

# Interpolate the data
grid = griddata(points, values, (grid_x, grid_y), method='linear')


print is_dark([350, 1, 0], axis_x, axis_y, grid)

# colors = [hsl_to_rgb(d) for d in data]
# for i, c in enumerate(colors):
#     colors[i] = [c[0]/255., c[1]/255., c[2]/255.]

# display_interpolation(grid_x, grid_y, grid)
# display_surface(points[:,0], points[:,1], values, colors)

