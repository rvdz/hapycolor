import subprocess as sp
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

    def export(palette, image_path):
        """Sets a wallpaper.

        :arg img: the image's path
        """
        path = pathlib.Path(image_path).expanduser()
        if not path.exists():
            msg = "Image not found: {}".format(image_path)
            raise exceptions.WrongInputError(msg)

        path = path.as_posix()
        os = targets.os()
        if os == targets.OS.DARWIN:
            Wallpaper._export_darwin(path)
        elif os == targets.OS.LINUX:
            Wallpaper._export_linux(path)

    def _export_linux(image_path):
        try:
            sp.run(['feh', '--bg-scale', image_path])
            return
        except Exception:
            pass
        try:
            sp.run(['gsettings', 'set',
                             'org.gnome.desktop.background', 'picture-uri',
                             "file:///" + image_path], shell=True)
        except Exception as exc:
            msg = "\nUnable to set the wallpaper\n{}".format(exc)
            raise exceptions.ExportTargetFailure(msg, Wallpaper)

    def _export_darwin(image_path):
        db_file = "~/Library/Application Support/Dock/desktoppicture.db"
        db_file = pathlib.Path(db_file).expanduser()
        if not db_file.is_file():
            msg = "\nUnable to set the wallpaper, sorry\n"
            raise exceptions.ExportTargetFailure(msg, Wallpaper)

        sp.run(["sqlite3",
                        db_file.as_posix(),
                        "update data set value = '{}'".format(image_path)])
        sp.run(["killall", "Dock"])
