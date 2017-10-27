import subprocess
import pathlib
from hapycolor import config

class Wallpaper:

    def set_macos(palette, name, img):
        """Set a wallpaper on macOS."""
        db_file = pathlib.Path(config.wallpaper_config()).expanduser()
        if not db_file.is_file():
            raise config.ExportTargetFailure("\nUnable to set the wallpaper, sorry\n", config.Target.WALLPAPER)

        subprocess.call(["sqlite3", db_file, "update data set value = '%s'" % img])
        subprocess.call(["killall", "Dock"])

