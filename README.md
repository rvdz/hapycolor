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
Hapyolor generates beautiful color palettes from images and exports them throughout your environment.
By using imagemagick and various clever filter algorithms it selects the best colors from a picture.
The full official documentation can be found [here](https://rvdz.github.io/hapycolor/).

## Requirements
- Debian or macOS.

### Dependencies
- linux or macOS (iTerm2)
- python 3.5+
- imagemagick
- scipy
- matplotlib (TODO: is it true?)

__Debian__:
```sh
sudo apt-get update && sudo apt-get install python3 python3-pip python3-scipy python3-matplotlib imagemagick -y
```

__macOS__:

With [homebrew](https://brew.sh/):
```sh
brew install python3 python3-pip python3-scipy python3-matplotlib imagemagick
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

To check if all the test pass on a Debian Stretch, you can build and run the provided dockerfile:
```sh
docker build -t hapycolor .
docker run -t hapycolor
```

### Installation
In order to install this project, run:
```sh
python3 setup.py install
```

### Run
To run the program execute:
```sh
hapycolor -f [path/to/file]
```
