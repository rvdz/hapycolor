Targets
========

.. role:: vim(code)
    :language: vim

.. role:: bash(code)
    :language: bash

Currently Supported Targets
---------------------------
- `Gnome Terminal`_
- `Vim`_
- `iTerm2`_
- `Wallpaper`_
- `Lightline`_

.. _Gnome Terminal:

Gnome Terminal
--------------

.. todo:: Write something here

.. _iTerm2:

iTerm2
------
This program is a replacement for Terminal and works on Macs with macOS 10.10 or newer.
iTerm2 brings the terminal into the modern age with features you never knew you always wanted.
For more information, please check their website_. It can be downloaded and installed from its
website_, or with homebrew_'s cask_ extension: :bash:`brew cask install iterm2`.

.. _homebrew: https://brew.sh/

.. _cask: https://caskroom.github.io/

.. _website: https://iterm2.com/

Hapycolor creates an iTerm's profile which is added to the terminal preferences'
file named after the provided image's name. A custom configuration file
must be used instead of the default one. To do so, enable the option
:code:`Load preferences from a custom folder or URL:` in iTerm's `Preferences -> General` menu and
select a target folder, then, when configuring hapycolor's target, enter the newly created configuration file.

In addition, this feature allows the user to choose whether or not the generated
profile should be set as the default profile.


.. note::
    By default, iTerm2 uses the configuration file located in: :code:`~/Library/Preferences/com.googlecode.iterm2.plist`,
    which is automatically encoded and therefore, would require additional operations in order to
    be altered. Maybe a future version of hapycolor will support the default file,
    but by now, it only manages a custom one, which is not encoded.

.. _Vim:

Vim
---
`Vim (Vi IMproved)`_ is a highly configurable text editor built to make creating and changing
any kind of text very efficient, compatible with most UNIX distributions. It can be installed
through your favorite package manager, which can be confirmed by running the command :bash:`vim --version`.

.. _Vim (Vi IMproved): http://www.vim.org/

Hapycolor is able to generate a colorscheme from a palette, with the condition
of providing, when initializing the target, a path where it will be installed
as a plugin. So, you should make sure that the plugin 'hapycolor' is enabled
in your environment.

To activate the generated colorscheme, use the command :vim:`colorscheme hapycolor` from the
`Ex` command line or in your `vimrc`.

Currently, it supports 8bit and 24bit color terminals, but by default, vim only
supports 8bit colors. If your terminal supports 24bit colors, it is highly advised
to set the option :vim:`set termguicolor`, available since Vim 7.4, in your vimrc.

.. todo:: Check if the option was introduced with Vim 7.4

.. _Wallpaper:

Wallpaper
---------

macOS
`````
Hapycolor allows you to automatically set the provided image as the wallpaper of the
current workspace. This target works only if `desktoppicture.db` exists in the
folder `~/Library/Application Support/Dock/`, which should be allways true.

.. todo:: Does anybody know if the previous assertion have exceptions?

Linux
`````

.. todo:: Write something here

.. _Lightline:

Lightline
---------
A light and configurable statusline/tabline plugin for Vim. To install this plugin,
please check itchyny_'s repository_.

.. _itchyny: https://github.com/itchyny

To enable this target, for a simple configuration, the following instruction should be
added to the vimrc:

.. code-block:: vim

    let g:lightline = {'colorscheme': 'hapycolor' }

For more information on how to configure this target, please check its repository_.

Then, hapycolor's initialization will require the user to enter the path of this plugin.

It currently supports various themes inspired from lightline's repository:

- Solarized
- Wombat
- One
- Landscape

In order to add new themes, a template should be added in :code:`hapycolor/targets/lightline_themes/`, written in
a flattened [1]_ format, as the other themes, and can use the following undefined variables:

- :vim:`s:blue`
- :vim:`s:magenta`
- :vim:`s:yellow`
- :vim:`s:red`
- :vim:`s:orange`
- :vim:`s:green`

.. [1] Each color of the theme must be defined as a pair 24bit and 8 bit color: `[ '#24bit_color', '8bit_color' ]`

.. _repository: https://github.com/itchyny/lightline.vim

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

Finally, the module's name needs to be imported into :mod:`targets`'s environment. In other words,
:code:`from . import <new_target_module>` must be added in :mod:`targets`.

.. todo:: Change -reconfigure- by its real command

.. note:: Maybe, in a near future, this last constraint could be removed by inspecting all the classes of the module
    and retrieving only the one that implements the abstract :class:`hapycolor.targets.base.Target`. This solution could
    perhaps, remove the need for a second step.
