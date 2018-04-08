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
    This abstract class is meant to be inherited by an object that needs to
    alters a file, for instance, a target that edits its configuration file
    such as i3 or yabar.

    In order to do so, it loads the associated file into a buffer and
    allocates an empty buffer which will store the new version of the file.
    Both are provided through a context manager and once the context closed,
    the new buffer will be saved in the target file.

    In between, each line of the file is matched to a provided regular
    expression, and, if a match is found, the matched line is replaced. This
    operation is performed by running the provided substitution function with
    the result of the match (:class:`re.match`).

    The reader might wonder why a function is required instead of a string
    when replacing a line. The answer comes from the fact that in some cases,
    parts of the former line are needed to create the new one. To do so, the
    user can provide a regular expression capturing the needed parts in
    addition of defining the targeted pattern and the result of the match
    will be used to generate the new line through the provided function.

    .. todo::
        We should change the name of this class, since it can be
        confused with :class:`ConfigurationManager`
    """
    def get_config_file():
        raise NotImplemented

    @contextlib.contextmanager
    def edit_config(cls):
        """
        This context manager first, loads the lines of the configuration file
        into a buffer and allocates an empty buffer. Then, both lists are
        passed to the created context, which should analyze the old buffer and
        fill the new one. Finally, once the context has been closed, the new
        buffer is written into the configuration file.
        """
        old_lines = []
        new_lines = []
        with open(cls.get_config_file(), 'r') as old_f:
            old_lines = old_f.readlines()

        yield (old_lines, new_lines)

        with open(cls.get_config_file(), 'w') as new_f:
            new_f.write(''.join(new_lines))

    @classmethod
    def replace_line(cls, pattern, substitution, *args):
        """
        Parses the configuration file, applying the provided pattern to each
        line. If a match is found, the :class:`re.match` object created is
        passed to the substitution function, which generates the new line
        that will replace the matched line.

        It might happen that the substitution function will need other
        arguments, such as a list of colors and an index, in the case of
        multiple substitutions with different colors. So, in order to
        generalize this tool, the substitution function can be prototyped
        as:

        ```
        def substitution(match, *args)
        ```

        When executing the substitution, the arguments will be the result
        of the match and :arg *args:

        .. note::
            For more details and examples, please check the tests in
            :func:`tests.test_configuration.TestConfiguration`

        .. warning::
            If any line matches the pattern,
            :func:`ContextEditor.replace_line()` it will call the substitution
            function providing 'None' as argument and add the result at the
            end of the file. This implies that the substitution function should
            manage the case where 'None' is provided instead of a
            :class:`re.match` object.
        """
        p = re.compile(pattern)
        match = False
        with ConfigurationEditor.edit_config(cls) as (config, new_config):
            for line in config:
                if p.match(line):
                    new_line = substitution(p.match(line), *args) + '\n'
                    new_config.append(new_line)
                    match = True
                else:
                    new_config.append(line)

            if not match:
                new_config.append(substitution(None, *args) + '\n')
