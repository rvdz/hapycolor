# Hapycolor

[![MIT licensed](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE.md)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)
[![shileds.io](https://img.shields.io/badge/built--with-vim-green.svg?style=for-the-badge)](http://shields.io)
[![Documentation Status](https://readthedocs.org/projects/hapycolor/badge/?version=latest)](https://hapycolor.readthedocs.io/en/latest/?badge=latest)


## What is Hapycolor?
Hapyolor generates beautiful color palettes from an input image and exports it
throughout your environment. The goal behind this project, is to create a tool
able to pick colors from an image, that are well suited to an editor's colorscheme
or a teminal's color profile. In addition, from the palette,
the colors should be automatically exported to targets selected by the user.

## What defines a suitable palette of colors?
First of all, if the purpose of those colors is to be used in a terminal or in
an editor, they shouldn't be too dark, nor too bright (except for the background or,
for some people, the foreground). Then, due to the low number of colors usually needed by the
targets (e.g., a terminal's profile only needs sixteen colors), compared to the
large number of colors of the original image, it is necessary to filter the colors
so that they are not "too close". For instance, if an image has multiple
shades of blue, the output should contain hues of blue that are easily
distinguishable.

## What targets are currently supported?
Currently, are supported:

__multiplatform__:
- Vim
- Lightline

__macOS__:
- iTerm

__Debian__ and __Ubuntu__:
- Gnome Terminal
- Rofi
- Yabar
- i3

For more details, The full documentation can be found [here](https://hapycolor.readthedocs.io/en/latest/).

### Dependencies
- python >= 3.5
- imagemagick
- feh (Linux only)

__Debian or Ubuntu__:
```sh
sudo apt-get update && sudo apt-get install python3 python3-pip imagemagick feh -y
```

__macOS__:

With [homebrew](https://brew.sh/):
```sh
brew install python3 python3-pip imagemagick
```

## Installation
Hapycolor can be installed with `pip`, or by cloning this repository.

### Pip install
```sh
pip3 install hapycolor
```

### Git install
```sh
git clone https://github.com/rvdz/hapycolor
cd hapycolor
pip3 install . --user
```

## Usage
For basic usage, execute:

```sh
hapycolor -f <path/to/file>
```

The full documentation of Hapycolor's cli can be found by running:

```sh
hapycolor --help
```

## Warnings
Gnome Terminal might not load the generated profile at first. In that
case:
- Create a new profile called 'Default', and switch to it
- OR run:
```sh
dconf reset -f /org/gnome/terminal/legacy/profiles:/
```

If one of the above solutions does not work for you (Debian 9,
Gnome shell 3.22 for instance), try doing both by reseting first.

## Test
To run the tests locally, excute:
```sh
python3 setup.py test
```
