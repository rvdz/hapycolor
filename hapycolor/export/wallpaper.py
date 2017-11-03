import subprocess
import pathlib
from hapycolor import config
from hapycolor import exceptions


class Wallpaper:

    def set_macos(palette, name, img):
        """Sets a wallpaper on macOS.

        Keyword arguments:
        img -- the image's path
        """
        db_file = pathlib.Path(config.wallpaper_config()).expanduser()
        if not db_file.is_file():
            msg = "\nUnable to set the wallpaper, sorry\n"
            raise exceptions.ExportTargetFailure(msg, config.Target.WALLPAPER)

        subprocess.call(["sqlite3", db_file, "update data set value = '%s'" % img])
        subprocess.call(["killall", "Dock"])
