import subprocess
import pathlib
from hapycolor import config
from hapycolor import exceptions
from . import base


class Wallpaper(base.Target):

    def initialize_config():
        return None

    def is_config_initialized():
        return True

    def compatible_os():
        return [config.OS.DARWIN]

    configuration_key = "wallpaper_macos"

    def export(palette, image_path):
        """Sets a wallpaper on macOS.

        :arg img: the image's path
        """
        db_file = pathlib.Path(Wallpaper.load_config()[Wallpaper.configuration_key]).expanduser()
        if not db_file.is_file():
            msg = "\nUnable to set the wallpaper, sorry\n"
            raise exceptions.ExportTargetFailure(msg, Wallpaper)

        full_path = pathlib.Path(image_path).resolve().as_posix()
        subprocess.call(["sqlite3", db_file, "update data set value = '%s'" % full_path])
        subprocess.call(["killall", "Dock"])
