from . import exceptions

import configparser
import pathlib
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
    return pathlib.Path(LOCAL_DIR / ("." + LOCAL_CONFIG)).expanduser().as_posix()


def get_default_config():
    return (ROOT_DIR / CONFIG).as_posix()


class ConfigurationManager:

    def load(section):
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
            raise exceptions.InvalidConfigKeyError("Configuration entry not found",
                                                   e)

        with open(get_config(), "w") as f:
            config.write(f)
