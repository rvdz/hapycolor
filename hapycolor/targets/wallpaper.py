import subprocess
import pathlib
import platform
from hapycolor import config
from hapycolor import exceptions
from . import base


class Wallpaper(base.Target):

    def initialize_config():
        return None

    def is_config_initialized():
        return True

    def compatible_os():
        return [config.OS.DARWIN, config.OS.LINUX]

    configuration_darwin = "wallpaper_macos"

    def export(palette, image_path):
        """Sets a wallpaper.

        :arg img: the image's path
        """
        os = config.os()
        if os == config.OS.DARWIN:
            Wallpaper.__export_darwin(image_path)
        elif os == config.OS.LINUX:
            Wallpaper.__export_linux(image_path)

    def __export_linux(image_path):
        try:
            subprocess.call(['feh', '--bg-scale', image_path])
            return
        except:
            pass
        try:
            subprocess.call(['gsettings', 'set', 'org.gnome.desktop.background', 'picture-uri', "file:///" + image_path])
        except:
            msg = '\nUnable to set the wallpaper\n'
            raise exceptions.ExportTargetFailure(msg, Wallpaper)


    def __export_darwin(image_path):
        value = Wallpaper.load_config()[Wallpaper.configuration_darwin]
        db_file = pathlib.Path(value).expanduser()
        if not db_file.is_file():
            msg = "\nUnable to set the wallpaper, sorry\n"
            raise exceptions.ExportTargetFailure(msg, Wallpaper)

        full_path = pathlib.Path(image_path).resolve().as_posix()
        subprocess.call(["sqlite3", db_file, "update data set value = '%s'" % full_path])
        subprocess.call(["killall", "Dock"])
