# Hapycolor

Some examples of badges:

[![MIT licensed](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE.md)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)
[![forthebadge](http://forthebadge.com/images/badges/built-with-love.svg)](http://forthebadge.com)
[![forthebadge](http://forthebadge.com/images/badges/contains-cat-gifs.svg)](http://forthebadge.com)
[![forthebadge](http://forthebadge.com/images/badges/kinda-sfw.svg)](http://forthebadge.com)
[![shileds.io](https://img.shields.io/badge/built--with-vim-green.svg?style=for-the-badge)](http://shields.io)

TODO: we could add a badge according to our code coverage: https://codecov.io/gh or https://coveralls.io

## What is Hapycolor?
Hapyolor generates beautiful color palettes from an input image and exports it
throughout your environment. The goal behind this project, is to create a tool
able to pick the colors that are representative of the image, but also well suited
to an editor's colorscheme or a teminal's color profile. In addition, from the palette,
the colors should automatically be available and exported to targets selected by the user.

## What defines a suitable palette of colors?
First of all, if the purpose of those colors is to be used in a terminal or in
an editor, they should'nt be too dark, nor too bright (except the background or
even the foreground). Then, due to the low number of colors usually needed by the
targets (e.g., a terminal's profile only needs sixteen colors), compared to the
number of colors in the original image, it is undesirable
to have colors that are "too close". For instance, if an image has multiple
shades of blue, the output should contain hues of blue that are easily
distinguishable, thus, reducing the total number of colors.

## What targets are currently supported?
Currently, are supported:

- Vim
- Gnome Terminal and iTerm
- Lightline themes
- Rofi
- Yabar
- i3

For more details, The full documentation can be found [here](https://rvdz.github.io/hapycolor/).

## Requirements
Tested on:

- Debian
- Ubuntu
- macOS.

### Dependencies
- python >=3.5
- imagemagick

__Debian__:
```sh
sudo apt-get update && sudo apt-get install python3 python3-pip imagemagick -y
```

__macOS__:

With [homebrew](https://brew.sh/):
```sh
brew install python3 python3-pip imagemagick
```

## Installation
Hapycolor can be installed with `pip`, or by cloning this repository.

### Pip install
TODO: Still not enabled
```sh
pip3 install hapycolor
```

### Git install
```sh
git clone https://github.com/rvdz/hapycolor
cd hapycolor
python3 setup.py install
```

If you don't have sudoers permissions, then run: (TODO: does it work?)
```sh
python3 setup.py install --user
```

Then, you should add the generated binary in your $PATH. To do so, execute
the following command or add it in your bashrc or zshrc.
```sh
export PATH=<path/to/bin>:$PATH
```
For more information, please check: [Installing Python Modules](https://docs.python.org/3.6/install/index.html#alternate-installation).

## Usage
To run the program execute:
```sh
hapycolor -f <path/to/file>
```

gnome-terminal:
    - create a new profile called 'Default', and switch to it
    - OR execute dconf reset -f /org/gnome/terminal/legacy/profiles:/
    (or replace the path with yours, but this is the default one)

!! If one of the above solutions does not work for you (Debian 9, 
   Gnome shell 3.22 for instance), try doing both by reseting first

## Tests
To run the tests locally, excute:
```sh
python3 tests/run_suite.py -v VERBOSITY
```

To run the tests on a clean Debian Stretch image, you can build and run
the provided dockerfile:
```sh
make build
make run
```

The created container can be stopped by running:
```sh
make stop
```
