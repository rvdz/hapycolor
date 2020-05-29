from . import base
from hapycolor import helpers
from sklearn.cluster import KMeans


class KMeansFilter(base.Filter):
    nb_colors = 16

    @staticmethod
    def apply(palette):
        """
        kmeans of X colors

        :arg palette: the input palette
        :return: the output palette
        :rtype: an instance of :class:`hapycolor.palette.Palette`
        """
        kmeans = KMeans(n_clusters=KMeansFilter.nb_colors, random_state=42).fit(palette.colors)
        colors = kmeans.cluster_centers_.astype(int).tolist()
        colors = [tuple(col) for col in colors]

        fg = max(colors, key=lambda col: helpers.rgb_to_hsl(col)[2])
        bg = min(colors, key=lambda col: helpers.rgb_to_hsl(col)[2])
        colors.remove(fg)
        colors.remove(bg)

        colors_by_hue = sorted(colors, key=lambda col: helpers.rgb_to_hsl(col)[0])

        colors = [[]]*(KMeansFilter.nb_colors - 2)
        get_sat = lambda col: helpers.rgb_to_hsl(col)[1]
        for i in range(len(colors_by_hue) // 2):
            colors[i] = max(colors_by_hue[2*i:2*(i+1)], key=get_sat)
            alt_i = i + (len(colors_by_hue) // 2)
            colors[alt_i] = min(colors_by_hue[2*i:2*(i+1)], key=get_sat)

        palette.colors = colors
        palette.foreground = fg
        palette.background = bg

        return palette
