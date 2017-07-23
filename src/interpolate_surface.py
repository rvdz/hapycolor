from scipy.interpolate import griddata
from  matplotlib import pyplot as plt
from utils import hsl_to_rgb
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import json
from sys import argv

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
    ax.scatter(X, Y, Z, c=colors) #, cmap=plt.cm.YlGnBu_r)
    plt.show()

# Set up grid
grid_x, grid_y = np.mgrid[-1:1:100j, -1:1:100j]

# Load the provided points
data = load_points(argv[1])
points, values = polar_to_cartesian(data)

# Interpolate
grid = griddata(points, values, (grid_x, grid_y), method='linear')

colors = [hsl_to_rgb(d) for d in data]
for i, c in enumerate(colors):
    colors[i] = [c[0]/255., c[1]/255., c[2]/255.]

display_interpolation(grid_x, grid_y, grid)
# display_surface(points[:,0], points[:,1], values, colors)

