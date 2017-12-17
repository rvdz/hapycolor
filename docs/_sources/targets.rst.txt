Targets
========

Currently Supported Targets
---------------------------
- `Gnome Terminal`_
- `Vim`_
- `iTerm`_
- `Wallpaper`_
- `Lightline`_

.. _Gnome Terminal:

Gnome Terminal
--------------

.. _iTerm:

iTerm
-----

.. _Vim:

Vim
---

.. _Wallpaper:

Wallpaper
---------

.. _Lightline:

Lightline
---------
A light and configurable statusline/tabline plugin for Vim (see github repository_).
For a simple configuration, add the following instruction in your vimrc:

.. _repository: https://github.com/itchyny/lightline.vim

.. code-block:: vim

    let g:lightline = {'colorscheme': 'hapycolor' }

It currently supports various themes inspired from lightline's repository:

- Solarized
- Wombat
- One
- Landscape

In order to add new themes, a template should be added in `hapycolor/targets/lightline_themes/`, written in
a flattened [1]_ format and can use the following undefined variables:

- s:blue
- s:magenta
- s:yellow
- s:red
- s:orange
- s:green

.. [1] Each color of the theme must be defined as a pair 24bit and 8 bit color: `[ '#24bit_color', '8bit_color' ]`

Those variables will then be defined when exporting a palette to the target.

How to add a target?
--------------------
In order to add a target, two steps are required:

First, a class extending :class:`hapycolor.targets.base.Target` needs
to be implemented in the module :class:`hapycolor.targets`. The main method, the static function :func:`export`, takes
in a palette of colors and exports it to the target. Other methods that should be implemented are:

- :func:`compatible_os`, which defines a list of compatible OS.
- :func:`initialize_config`, which interacts with the user and stores in its respective section of the configuration file
  persistent data needed to export a palette.
- :func:`reconfigure`. This method can be triggered by hapycolor's -reconfigure- option, which asks for the name of the
  target's module to reconfigure. To do so, it currently searches for a class that matches the module's name implemented in
  it, except, named in PascalCase, rather than snake_case in the case of the module.

Finally, the module's name needs to be added to :class:`targets`'s environment. In other words, the `__all__` list
defined in :class:`targets.__init__` shoud be altered to include the new target.

.. todo:: Change -reconfigure- by its real command

.. note:: Maybe, in a near future, this last constraint could be removed by inspecting all the classes of the module
    and retrieving only the one that implements the abstract :class:`hapycolor.targets.base.Target`. This solution could
    perhaps, remove the need for a second step.
