# Export to targets

## Wallpaper

### Linux

Requires either ```feh``` or ```gsettings```. ```feh``` option is ```--bg-scale```.

TODO: test with ```gsettings``` (does not work on my Deb).

## Yabar

You must specify the path to your yabar config file during the initialization,
as well as the default hue for the use defined below.

Your config file must follow the following requirements:
 - RGB colors must be written as 0x$TOKEN
 - ARGB colors must be written as 0xA$TOKEN
Where A refers to the hex alpha value (00 to FF), and $TOKEN refers to the
token the script will look for.

Possible tokens are:
 - $TBG for the background color
 - $TFG for the foreground color
 - $RC for a total random color (not twice the same, so if you have more than
   16 $RC in your config file, it will most likely crash)
 - $DCTx for a color the closest to the hue specified by 'x' (0 to 360)
 - $DCxTx for a color in the hue range specified by the two 'x' ($DC30T60 for
   a color between the hue 30 and the hue 60). If no color can be found, it uses
   the closest color to the default hue specified at initialization.
