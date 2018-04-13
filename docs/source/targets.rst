Targets
========

.. contents::

.. role:: vim(code)
    :language: vim

.. role:: bash(code)
    :language: bash

.. role:: python(code)
    :language: python

Gnome Terminal
--------------

.. todo:: Write something here

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
``Load preferences from a custom folder or URL:`` in iTerm's ``Preferences -> General`` menu and
select a target folder, then, when configuring hapycolor's target, enter the newly created configuration file.

In addition, this feature allows the user to choose whether or not the generated
profile should be set as the default profile.

.. note::
    For some themes, you might want to switch to the dark mode, to do so, go to Preferences > Appearance and in
    the `Theme:`'s menu, select `Dark`.

.. note::
    By default, iTerm2 uses the configuration file located in: :code:``~/Library/Preferences/com.googlecode.iterm2.plist``,
    which is automatically encoded as an `Apple binary property list`_. It is possible to use a custom file by enabling
    ``Load preferences from a custom folder or URL:`` in ``Preferences > General > Preferences``, and selecting a target folder.
    Then, when configuring hapycolor, you will have to provide the path to the generated custom preferences file.

.. _`Apple binary property list`: https://en.wikipedia.org/wiki/Property_list

Vim
---
`Vim (Vi IMproved)`_ is a highly configurable text editor built to make creating and changing
any kind of text very efficient, compatible with most UNIX distributions. It can be installed
with your favorite package manager, which can be confirmed by running the command :bash:`vim --version`.

.. _Vim (Vi IMproved): http://www.vim.org/

When configuring this target, if you are using common paths to manage your plugins, such as
``~/.vim/bundle``, ``~/.vim_runtime/sources_non_forked`` or ``~/.vim_runtime/sources_forked``,
hapycolor should automatically install the colorscheme. Else, you will be prompted to input
the path of the location where the plugin should be installed. If you are not using any plugin manager,
enter the following commands in your vimrc:

.. code-block:: vim

    ! Using plug
    Plug 'hapycolor'

To activate the generated colorscheme, use the command :vim:`colorscheme hapycolor` from the
``Ex`` command line or add it to your ``vimrc``.

Currently, it supports 8bit and 24bit color terminals. By default, vim only
supports 8bit colors, but if your terminal supports 24bit colors, it is highly advised
to set the option :vim:`set termguicolor`, available since Vim 7.4, in your vimrc.

.. todo:: Check if the option was introduced with Vim 7.4

Wallpaper
---------

macOS
`````
Hapycolor allows you to automatically set the provided image as the wallpaper of the
current workspace. This target works only if ``desktoppicture.db`` exists in the
folder ``~/Library/Application Support/Dock/``, which should be allways true.

.. todo:: Does anybody know if the previous assertion have exceptions?

Linux
`````

.. todo:: Write something here

Lightline
---------
A light and configurable statusline/tabline plugin for Vim. To install this plugin,
please check itchyny_'s repository_.

.. _itchyny: https://github.com/itchyny

To enable this target, for a simple configuration, the following instruction should be
added to the vimrc:

.. code-block:: vim

    let g:lightline = {'colorscheme': 'hapycolor' }

By default, Vim displays the current mode (except for 'normal') in the bottom left section of the editor,
to disable it, use: :vim:`set showmode!`.
For more information on how to configure this target, please check its repository_.

Then, hapycolor's initialization will require the user to enter the path of this plugin.

It currently supports various themes inspired from lightline's repository:

- Solarized
- Wombat
- One
- Landscape

In order to add new themes, a template should be added in ``hapycolor/targets/lightline_themes/``, written in
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

i3
--
The class :class:`hapycolor.targets.i3.I3` implements three features:

- Sets the border and split colors. Currently it defines two variables,
    `$split_color` and `$border_color` and sets the i3's variable
    `client.focused`. This last variable asks for four colors: the border,
    the background, the text and the split color, but currently it only
    defines the border, background with `$border_color` and the split color
    with, as you guessed, `$split_color`, leaving the text color unaltered.
    There are other options regarding i3's colors: `client.focused_inactive`,
    `client.unfocused`, `client.urgent` and `client.background`, but this
    class does not supports them yet.
- Inserts yabar's execution command into i3's configuration, if yabar is
    enabled
- Inserts `feh`'s command in order to set the wallpaper, if this target was
    enabled

How to add a target?
--------------------
In order to add a target, two steps are required:

First, a class extending :class:`hapycolor.targets.base.Target` needs
to be implemented in the module :class:`hapycolor.targets`. The main method, the static function :func:`hapycolor.targets.base.Target.export`, takes
in a palette of colors and exports it to the target. Other methods that should be implemented are:

- :func:`hapycolor.targets.base.Target.compatible_os`, which defines a list of compatible OS.
- :func:`hapycolor.targets.base.Target.initialize_config`, which interacts with the user and stores in its respective section of the configuration file
  persistent data needed to export a palette.
- :func:`hapycolor.targets.base.Target.reconfigure`. This method can be triggered by hapycolor's -reconfigure- option, which asks for the name of the
  target's module to reconfigure. To do so, it currently searches for a class that matches the module's name implemented in
  it, except, named in PascalCase, rather than snake_case in the case of the module.

Finally, the module's name needs to be imported into :mod:`hapycolor.targets`'s environment. In other words,
:python:`from . import <new_target_module>` must be added in :mod:`hapycolor.targets`.

.. todo:: Change -reconfigure- by its real command

.. note:: Maybe, in a near future, this last constraint could be removed by inspecting all the classes of the module
    and retrieving only the one that implements the abstract :class:`hapycolor.targets.base.Target`. This solution could
    perhaps, remove the need for a second step.
