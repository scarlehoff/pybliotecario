"""
    Base/abstract backend class

    Each backend should implement its own message type
"""

from abc import ABC, abstractmethod
import logging
import json

logger = logging.getLogger(__name__)


class Message(ABC):
    """
    Base message class

    Any implementation of the message should either save a dictionary
    ``_message_dict`` with the following attributes (through _parse_update)
    or implement its own way of getting the different values
    """

    _type = "Abstract"
    _original = None

    _message_dict = {
        "chat_id": None,
        "username": None,
        "command": None,
        "file_id": None,
        "text": None,
        "ignore": False,
    }

    def __init__(self, update):
        self._original = update
        self._parse_update(update)
        # After the information is parsed, log the message!
        logger.info("New message: %s", self)

    def __str__(self):
        return json.dumps(self._message_dict)

    @abstractmethod
    def _parse_update(self, update):
        return None

    @property
    def chat_id(self):
        return self._message_dict["chat_id"]

    @property
    def username(self):
        return self._message_dict["username"]

    @property
    def text(self):
        return self._message_dict.get("text")

    @property
    def is_command(self):
        return self._message_dict.get("command") is not None

    @property
    def command(self):
        return self._message_dict.get("command")

    @property
    def is_file(self):
        return self._message_dict.get("file_id") is not None

    @property
    def file_id(self):
        return self._message_dict.get("file_id")

    @property
    def has_arguments(self):
        return self.is_command and self.text is not None

    @property
    def ignore(self):
        return self._message_dict.get("ignore", False)

    @ignore.setter
    def ignore(self, val):
        self._message_dict["ignore"] = val
