import re
import pathlib
import subprocess
import contextlib
import os
from hapycolor import exceptions


class VimEnvironments:
    def is_vim_installed():
        try:
            subprocess.run(["vim", "--version"], stdout=subprocess.DEVNULL)
            return True
        except FileNotFoundError:
            return False

    def bundle_plugins_path():
        common_paths = ["~/.vim/bundle", "~/.vim/pack/bundle/start",
                        "~/.vim_runtime/sources_non_forked"]
        common_paths = [pathlib.Path(p) for p in common_paths]
        for p in common_paths:
            if p.expanduser().exists():
                return p.expanduser()
        raise exceptions.NoCommonPathFound("Common bundle's path do not exist")

    def plugin_paths():
        """
        Generates a file containing all the plugins' paths, and removes
        afterward.
        """

        plugin_paths = pathlib.Path("./plugin_paths.txt") \
                              .expanduser() \
                              .as_posix()

        vimscript = pathlib.Path("./hapycolor/targets/active_plugins.vim") \
                           .expanduser() \
                           .as_posix()

        subprocess.run(["vim", "-s", vimscript],
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)

        with open(plugin_paths, 'r') as pp:
            plugins = pp.readlines()
        os.remove(plugin_paths)

        plugins = plugins[0].split('=')[1].split(',')
        return plugins

    def find_plugin(plugin):
        """
        Retrives the full path to a vim plugin.

        :param plugin: a string representing the name of the plugin
        :return: None if the plugin is not found, otherwise the path of the
            provided plugin
        """
        plugins = VimEnvironments.plugin_paths()
        pattern = re.compile(r".*/{}$".format(plugin))
        for p in plugins:
            if pattern.match(p):
                return p
        return None
