Target
======

Currently Supported Targets
---------------------------
- Gnome Terminal
- Vim
- iTerm
- Wallpaper
- Lightline

iTerm
-----

Vim
---

Wallpaper
---------

Lightline
---------
A light and configurable statusline/tabline plugin for Vim (repo_).
For a simple configuration, add the following instruction in your vimrc:

.. _repo: https://github.com/itchyny/lightline.vim

.. code-block:: vim

    let g:lightline = {'colorscheme': 'hapycolor' }

It currently supports various themes inspired from lightline's repository:
- Solarized
- Wombat
- One
- Landscape

In order to add new themes, a template should be added in `hapycolor/targets/lightline_themes`, written in
a flattened [1]_ format and can use the following undefined variables:
- s:blue
- s:magenta
- s:yellow
- s:red
- s:orange
- s:green

.. [1] Each color of the theme must be defined as a pair 24bit and 8 bit color: `[ '#24bit_color', '8bit_color' ]`

Those variables will be then defined when exporting a palette to the target.

How to add a target?
--------------------
TODO
