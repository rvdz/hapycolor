How to Contribute
=================

.. role:: python(code)
    :language: python

We would love to have you contribute to the project! There are several ways that you can do so.

How to contribute without coding
--------------------------------

- **Suggest improvements**: Post bugs and enhancement requests at the `Github Issue List`_.

.. _`Github Issue List`: https://github.com/rvdz/hapycolor/issues

How to contribute code
----------------------

Filters
^^^^^^^
See: :ref:`add filters`.

Targets
^^^^^^^
See: :ref:`add targets`.

Useful Tools when contributing with code
----------------------------------------

There are a few useful classes implemented in this project when building
new targets:

Partitioning Around Medoids
^^^^^^^^^^^^^^^^^^^^^^^^^^^

:class:`hapycolor.targets.pam.PAM` - The k-medoids algorithm is a clustering
algorithm related to the k-means algorithm and the medoidshift algorithm. Both
the k-means and k-medoids algorithms are partitional (breaking the dataset up
into groups) and both attempt to minimize the distance between colors labeled
to be in a cluster and a color designated as the center of that cluster. In
contrast to the k-means algorithm, k-medoids chooses datapoints as centers
(medoids).

Many targets require a subset of colors from the palette, and usually, a
clever way to get them is to split the colors into clusters and retrieve the
center of each cluster with the constraint that this center must be a real
color of the palette. That way, at the end of the algorithm, we end up with
a defined number of centers that are sufficiently far appart.

.. note::
    The most common realisation of k-medoid clustering is the
    Partitioning Around Medoids (PAM) algorithm.

.. _`configuration editor`:

Configuration Editor
^^^^^^^^^^^^^^^^^^^^

:class:`hapycolor.configuration_editor.ConfigurationEditor` - Some targets like
i3 or yabar, rely on a configuration file which maps colors to elements of
the target. For instance, in i3's configuration, it is possible to define the
color of the borders. In order to create a generic tool able to deal with these
kind of targets, Hapycolor implements an editor able to identify and replace colors
marked by a "macro". This mark indicates that the next color will have to be
replaced when exporting the color to this target. Following the previous example,
if a user wants to automatically update the border color of i3's windows
with a color of the generated palette, he or she will have to mark
the line that precedes the target line with a comment line similar to:

.. code-block:: shell

    # @hapycolor(args)

The provided arguments specify which color has to be replaced
by which color. For instance, if there is only one color which
has to be replaced by the generated foreground color (resp. background),
then the argument will only be: "foreground" (resp. "background").
If the user wants to use another color from the palette, then use:
"random".

In some cases, there might be multiple colors on the same line,
but only a few of them have to be replaced, for instance:

.. code-block:: shell

    set colors #010203 #020304 #040506

Here, the first color should be replaced by the foreground, and
the last, should be replaced by a color of the palette. In this
case, the macro should look like:

.. code-block:: shell

    # @hapycolor("foreground", None, "random")
    set colors #010203 #020304 #040506

Finally, the palette object has an additional attribute
:attr:`hapycolor.palette.Palette.other`
which defines a dictionary whose keys can be used as macro's arguments
and its values will be the colors used for the colors marked with
the macro. For instance, :class:`hapycolor.targets.yabar.Yabar` evaluates
the average luminosity of the top 5% section of the image so that
the color of the text can be visible on top of the wallpaper.
If the image is bright (resp. dark) the couple
:python:`("yabar_foreground", (0, 0, 0))`
(resp. :python:`("yabar_foreground", (255, 255, 255))`)
That way, when parsing Yabar's configuration:

.. code-block:: c

    /* @hapycolor("yabar_foreground") */
    foreground-color-rgb: 0x000000;

The foreground color will be set to white (resp. black) if the top section
of the wallpaper is dark (resp. bright).


Terminal Color Manager
^^^^^^^^^^^^^^^^^^^^^^

:class:`hapycolor.targets.terminal_color_manager.TerminalColorManager` -
when implementing a class adding the support to a terminal emulator,
the generated profile will usually look the same: sixteen base colors,
among which 8 hues and for each hue, a bright and a darker color.
This class requires the list of at least fourteen colors and provides two
main methods:

- :func:`hapycolor.targets.terminal_color_manager.TerminalColorManager.cast_all`,
    which returns a list of colors (the second eight colors
    are the brighter version of each first eight colors).
- :func:`hapycolor.targets.terminal_color_manager.TerminalColorManager.cast`,
    which returns the ith color a the previously described list.

.. note::
   This class is already being used in the modules
   :class:`hapycolor.targets.gnome_terminal.GnomeTerminal` and
   :class:`hapycolor.targets.iterm.Iterm`
