from scipy import interpolate
from  matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import sys
import utils

class ColorFilter():

    def __init__(self):
        dark_hyperplan   = "../hyperplan_robin/dark.json"
        bright_hyperplan = "../hyperplan_robin/light.json"
        grey_hyperplan   = "../hyperplan_yann/saturations.json"

        # Set up grid
        grid_x, grid_y = np.mgrid[-1:1:100j, -1:1:100j]
        self.X         = [x[0] for x in grid_x]
        self.Y         = grid_y[0]

        # TODO: The following steps could be avoided if the generated hyperplan was stored in the disk
        # and then loaded entirely when creating an object of this class

        # Load the provided points
        dark_data   = utils.load_json(dark_hyperplan)
        bright_data = utils.load_json(bright_hyperplan)
        grey_data   = utils.load_json(grey_hyperplan)

        # Convert points to catesian
        dark_points   = np.asarray([self.__polar_to_cartesian(e[0], e[1]) for e in dark_data])
        dark_values   = [e[2] for e in dark_data]

        bright_points = np.asarray([self.__polar_to_cartesian(e[0], e[1]) for e in bright_data])
        bright_values = [e[2] for e in bright_data]

        # Interpolate the data
        self.dark_Z   = interpolate.griddata(dark_points, dark_values, \
                                        (grid_x, grid_y),              \
                                        method='linear')

        self.bright_Z = interpolate.griddata(bright_points, \
                                        bright_values,      \
                                        (grid_x, grid_y),   \
                                        method='linear')

        self.grey_interpolation = self.__interpolate_saturations([e[0] for e in grey_data],   \
                                                                   [e[1] for e in grey_data], \
                                                                   [e[2] for e in grey_data])


    def __interpolate_saturations(self, H, S, L):
        """ Interpolate saturation's cylinder with the provided colors. It starts by interpolating
            the saturation for the different luminosities and for a fixed hue. Then, it loops over a
            discretisation of the luminosity and for each of these values, it generates set(H) couples
            (sat,hue) with the functions defined in the previous step. With these couples, it finally
            interpolates a 2D deformed circle over the plan (x,y,z = l). """
        # Generates a function which for a fixed hue returns the image of the luminosity: f(l) = s
        F = []
        for h in set(H):
            tmp = [(L[i], S[i]) for i in range(len(H)) if H[i] == h]

            # Sorting the saturations according to the luminosities
            tmp.sort(key=lambda x: x[0])

            F.append(interpolate.interp1d([e[0] for e in tmp], [e[1] for e in tmp]))

        # For each discretisation of the luminosity, interpolates a 2D graph
        interpolation = {}
        for l in np.linspace(0, 1, 100):
            sat = [f(l) for f in F]
            # Convert to cartesian (sat, hues)
            surface = []
            for i, h in enumerate(set(H)):
                surface.append(self.__polar_to_cartesian(h, sat[i]))

            x = [e[0] for e in surface]
            x.append(x[0])
            y = [e[1] for e in surface]
            y.append(y[0])

            tck, u = interpolate.splprep([x, y], s=0)
            unew = np.arange(0, 1.01, 0.01)
            interpolation[l] = interpolate.splev(unew, tck)
        return interpolation


    def __polar_to_cartesian(self, r, theta):
        return r * np.cos(np.radians(theta)), r * np.sin(np.radians(theta))


    def display_interpolation(self, X, Y, Z):
        """ Displays the wireframe of a surface """
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_wireframe(X, Y, Z) #, cmap=plt.cm.YlGnBu_r)
        plt.show()


    def display_surface(self, X, Y, Z, colors):
        """ Displays a scatter plot where each color is represented by a
        a color of the given list """
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(X, Y, Z)
        plt.show()


    def __find_nearest_index(self, value, vector):
        i = 0
        for i, v in enumerate(vector):
            if v > value:
                return i
        return i


    def __find_nearest_point(self, P, surface_values):
        """ Returns the luminosity of the nearest interpolated point of
            the given point P """
        real_points = []
        for i in range(len(self.X)):
            # Search nearest point of the upper portion of the circle
            j = 0
            while surface_values[i, j] !=  surface_values[i, j]:
                # If there are no values along this axis
                j += 1
                if j + 1 > len(self.Y):
                    break

            # If there are no values along this axis
            if j + 1 > len(self.Y):
                continue

            real_points.append((i, j))
            # Search nearest point of the lower portion of the circle
            j = len(self.Y) - 1
            while surface_values[i, j] != surface_values[i, j]:
                j -= 1
            real_points.append([i, j])

        distance = sys.maxsize
        nearest_point = ()
        for p in real_points:
            if self.__get_2d_distance(P, p) < distance:
                distance = self.__get_2d_distance(P, p)
                nearest_point = p
        return surface_values[nearest_point[0], nearest_point[1]]


    def __get_2d_distance(self, p1, p2):
        return pow(p1[0] - p2[0], 2) + pow(p1[1] - p2[1], 2)


    def __project_point(self, x, y, surface_values):
        index_x = self.__find_nearest_index(x, self.X)
        index_y = self.__find_nearest_index(y, self.Y)

        interpol_value = surface_values[index_x, index_y]

        # If there are no interpolated values for this point, find the nearest
        if interpol_value != interpol_value:
            interpol_value = self.__find_nearest_point((x, y), surface_values)

        return interpol_value


    def is_too_bright(self, hsl_color):
        """ Returns a boolean depending if the given color is too bright.
            The color provided must be in hsl format"""
        x, y =  self.__polar_to_cartesian(hsl_color[0], hsl_color[1])
        return hsl_color[2] > self.__project_point(x, y, self.bright_Z)


    def is_too_dark(self, hsl_color):
        """ Returns a boolean depending if the given color is too dark.
            The color provided must be in hsl format"""
        x, y =  self.__polar_to_cartesian(hsl_color[0], hsl_color[1])
        return hsl_color[2] < self.__project_point(x, y, self.dark_Z)


    def __is_in_saturated_area(self, x, y, interpolation):
        """ Checks first if the color is not in the square delimited by the minima
            of the interpolation, if not, checks if it is in the deformed circle. """
        if (x < min(interpolation[0]) or x > max(interpolation[0])) \
                or (y < min(interpolation[1]) or y > max(interpolation[1])):
            return False

        epsilon = interpolation[0][1] - interpolation[0][0]
        Y = []
        for i, tmp_x in enumerate(interpolation[0]):
            if abs(tmp_x - x) < epsilon:
                Y.append(interpolation[1][i])

        Y.sort()
        try:
            return Y[0] < y and y < Y[1]
        except IndexError:
            return False


    def is_too_saturated(self, hsl_color):
        """ Checks if the color is saturated enough. The first step consist in finding the
            closest discretised luminosity and then, analyzing the interpolation of the
            (saturations, hues) for the previous luminosity. """
        keys = list(self.grey_interpolation.keys())
        epsilon = keys[1] - keys[0]
        x, y =  self.__polar_to_cartesian(hsl_color[0], hsl_color[1])
        for l in self.grey_interpolation:
            if abs(l - hsl_color[2]) < epsilon:
                return self.__is_in_saturated_area(x, y, self.grey_interpolation[l])
