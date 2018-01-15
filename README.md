# hapycolor
Generates beautiful color palettes from images.

hapycolor uses imagemagick and various filter algorithms to select the best colors from a picture.

## Usage
### Requirements
- Debian Stretch or macOS Sierra

### Dependencies
- python3 (> 3.6.2)
- imagemagick (> 7.0.6)

__Python packages__:
- colormath (> 2.1.1)
- scipy (> 0.19.1)
- matplotlib (> 2.0.2)
- numpy (> 1.13.1)
- Pillow (> 4.2.1)

__Other__:
- gcc
- OpenCV (3.3.0) [macOS](https://www.pyimagesearch.com/2016/12/19/install-opencv-3-on-macos-with-homebrew-the-easy-way/), [Debian](http://milq.github.io/install-opencv-ubuntu-debian/)

__Install python dependencies with pip__(> 9.0.1):
```sh
pip3 install colormath scipy matplotlib numpy Pillow
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


gnome-terminal:
    - create a new profile called 'Default', and switch to it
    - OR execute dconf reset -f /org/gnome/terminal/legacy/profiles:/
    (or replace the path with yours, but this is the default one)

!! If one of the above solutions does not work for you (Debian 9, 
   Gnome shell 3.22 for instance), try doing both by reseting first
