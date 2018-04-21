from . import exceptions

import configparser
import contextlib
import pathlib
import re
import shutil


ROOT_DIR = pathlib.Path(__file__).parent
CONFIG = "hapycolor.config"

# To be overwritten if the user wants to use a custom configuration file
LOCAL_DIR = pathlib.Path("~")
LOCAL_CONFIG = CONFIG


def create_config():
    """
    Creates a local configuration from the default one, in the user's base
    directory
    """
    dst = get_config()
    if not pathlib.Path(dst).is_file():
        shutil.copyfile(get_default_config(), dst)


def get_config():
    return pathlib.Path(LOCAL_DIR / ("." + LOCAL_CONFIG)) \
            .expanduser() \
            .as_posix()


def get_default_config():
    return (ROOT_DIR / CONFIG).as_posix()


class ConfigurationManager:
    """
    This class is meant to be inherited by a class that interacts with
    hapycolor's configuration file. It provides the basic methods to read
    and write in it.

    .. todo::
        We should change the name of this class, since it can be
        confused with :class:`ConfigurationManager`
    """

    def load(section):
        """
        Loads the content of a given section of hapycolor's configuration file

        :raises: :class:`InvalidConfigKeyError` when a section is not defined
            in the configuration file.
        """
        config = configparser.ConfigParser()
        config.read(get_config())
        try:
            return config[section]
        except KeyError as e:
            msg = "Configuration entry not found"
            raise exceptions.InvalidConfigKeyError(msg, e)

    def save(section, target_config):
        """
        Save a new entry in the config file.

        :arg section: a string representing a section in the configuration file
        :arg key: a string representing an entry in the given section
        :arg value: the value relative to the key to be added in the project's
            configuration file
        """
        config = configparser.ConfigParser()
        config.read(get_config())

        try:
            if section not in config:
                config[section] = target_config
            else:
                for key in target_config:
                    config[section][key] = str(target_config[key])
        except KeyError as e:
            msg = "Configuration entry not found"
            raise exceptions.InvalidConfigKeyError(msg, e)

        with open(get_config(), "w") as f:
            config.write(f)


class ConfigurationEditor:
    """
    This abstract class is meant to be a tool useful when a target needs to
    alter a file, for instance, i3 or yabar need to update their configuration
    file.

    .. see:: :func:`replace_line()`

    .. todo::
        We should change the name of this class, since it can be
        confused with :class:`ConfigurationManager`
    """
    @contextlib.contextmanager
    def edit_config(file):
        """
        This context manager first, loads the lines of the provided file
        into a buffer and allocates an empty buffer. Then, both lists are
        passed to the new context, which should read the old buffer and
        fill the new one. Finally, once the context has been closed, the new
        buffer is written into the file.
        """
        old_lines = []
        new_lines = []
        with open(file, 'r') as old_f:
            old_lines = old_f.readlines()

        yield (old_lines, new_lines)

        with open(file, 'w') as new_f:
            new_f.write(''.join(new_lines))

    def replace_line(file, pattern, substitution, *args):
        """
        Parses the provided file, applying the provided pattern to each
        line. If a match is found, the :class:`re.match` object created is
        passed to the substitution function, which generates the new line
        that will replace the matched line.

        It might happen that the substitution function will need other
        arguments. For instance: a list of colors and an index, where the index
        is incremented after each call, which allows the substitution function
        to replace the same matched pattern with different colors.
        So, in order to generalize this tool, the substitution function
        can be prototyped as:

        After running this function, the boolean `True` is returned
        if a match has been found, otherwise, `False`.

        .. code:: python

            def substitution(match, *args)

        Note, that the argument: `*args` is optional.

        .. note::
            For more details and examples, please check the tests in
            :class:`tests.test_configuration.TestConfiguration`
        """
        p = re.compile(pattern)
        match = False
        with ConfigurationEditor.edit_config(file) as (config, new_config):
            for line in config:
                if p.match(line):
                    new_line = substitution(p.match(line), *args)
                    new_config.append(new_line)
                    match = True
                else:
                    new_config.append(line)
        return match
