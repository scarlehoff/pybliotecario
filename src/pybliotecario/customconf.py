"""
    Define custom parsers for the config reader
    and default data/config locations
"""
from configparser import ConfigParser
from copy import copy
from os import environ
from pathlib import Path

NAME = "pybliotecario"


def default_config_path(name=NAME):
    """Return the default config path looking at the value of XDG_CONFIG_HOME
    Usually: $HOME/.config/pybliotecario/pybliotecario.ini
    """
    config_folder = Path(environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return config_folder / name / "pybliotecario.ini"


def default_data_path(name=NAME):
    """Return the default data path looking at the value of XDG_DATA_HOME
    Usually: $HOME/.local/share/pybliotecario
    """
    data_folder = Path(environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return data_folder / name


def _parse_chat_id(value):
    """The chat id can come as a list or as a single value,
    this ensures that it is always read as a list"""
    split_values = value.split(",")
    return [int(i.strip()) for i in split_values]


def _parse_main_chat_id(value):
    """Regardless of the format of the chat id (list or single value)
    return the main id (i.e., the only one there is or the first one
    """
    return _parse_chat_id(value)[0]


class CustomConfigParser(ConfigParser):
    """Equal to ConfigParser with a number of predefined converters"""

    def __init__(self, *args, converters={}, allow_no_value=True, **kwargs):
        new_converters = copy(converters)
        new_converters.setdefault("idlist", _parse_chat_id)
        new_converters.setdefault("mainid", _parse_main_chat_id)
        super().__init__(*args, converters=new_converters, allow_no_value=allow_no_value, **kwargs)
