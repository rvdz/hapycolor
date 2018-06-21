import subprocess
import pathlib
import platform
from hapycolor import targets
from hapycolor import exceptions
from . import base


class Wallpaper(base.Target):

    def initialize_config():
        return None

    def is_config_initialized():
        return True

    def compatible_os():
        return [targets.OS.DARWIN, targets.OS.LINUX]

    configuration_darwin = "wallpaper_macos"

    def export(palette, image_path):
        """Sets a wallpaper.

        :arg img: the image's path
        """
        path = None
        try:
            path = pathlib.Path(image_path).resolve().as_posix()
        except FileNotFoundError:
            msg = "Image not found: {}".format(image_path)
            raise exceptions.WrongInputError(msg)

        os = targets.os()
        if os == targets.OS.DARWIN:
            Wallpaper._export_darwin(path)
        elif os == targets.OS.LINUX:
            Wallpaper._export_linux(path)

    def _export_linux(image_path):
        try:
            subprocess.run(['feh', '--bg-scale', image_path])
            return
        except Exception:
            pass
        try:
            subprocess.run(['gsettings', 'set',
                             'org.gnome.desktop.background', 'picture-uri',
                             "file:///" + image_path])
        except Exception:
            msg = '\nUnable to set the wallpaper\n'
            raise exceptions.ExportTargetFailure(msg, Wallpaper)

    def _export_darwin(image_path):
        value = Wallpaper.load_config()[Wallpaper.configuration_darwin]
        db_file = pathlib.Path(value).expanduser()
        if not db_file.is_file():
            msg = "\nUnable to set the wallpaper, sorry\n"
            raise exceptions.ExportTargetFailure(msg, Wallpaper)

        subprocess.run(["sqlite3",
                        db_file.as_posix(),
                        "update data set value = '{}'".format(image_path)])
        subprocess.run(["killall", "Dock"])
