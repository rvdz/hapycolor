import re
import pathlib
import subprocess
import contextlib
import os
from hapycolor import exceptions


class VimHelpers:
    def is_vim_installed():
        try:
            subprocess.run(["vim", "--version"], stdout=subprocess.DEVNULL)
            return True
        except FileNotFoundError:
            return False

    def bundle_plugins_path():
        common_paths = [pathlib.Path(p) for p in ["~/.vim/bundle",
                                                  "~/.vim/pack/bundle/start",
                                                  "~/.vim_runtime/sources_non_forked"]]
        for p in common_paths:
            if p.expanduser().exists():
                return p.expanduser()
        raise exceptions.NoCommonPathFound("Common bundle's path do not exist")

    @contextlib.contextmanager
    def export_plugin_paths():
        """
        Generates a file containing all the plugins' paths, and removes
        afterward.
        """

        plugin_paths = pathlib.Path("./hapycolor/targets/plugin_paths.txt") \
                              .expanduser() \
                              .as_posix()

        vimscript = pathlib.Path("./hapycolor/targets/active_plugins.vim") \
                           .expanduser() \
                           .as_posix()

        subprocess.run(["vim", "-s", vimscript, plugin_paths],
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        yield plugin_paths
        os.remove(plugin_paths)

    def find_plugin(plugin):
        """
        Retrives the full path to a vim plugin.

        :param plugin: a string representing the name of the plugin
        :return: a string containing the full path of the plugin
        """
        with VimHelpers.export_plugin_paths() as path:
            with open(path) as f:
                plugins = f.readlines()
        p = re.compile("[0-9]+: (.*" + plugin + "/)")
        matches = [m for m in [p.search(l) for l in plugins] if m is not None]
        try:
            path = pathlib.Path(matches[0].group(1))
            return path
        except IndexError as e:
            msg = "No active plugin found named: " + plugin + " - " + str(e)
            raise exceptions.PluginError(msg)
