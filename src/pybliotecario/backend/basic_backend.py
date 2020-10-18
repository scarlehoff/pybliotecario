"""
    Base/abstract backend classes:

    - Message
    - Backend

    Each backend should implement its own message type and inherit from backend
"""

from abc import ABC, abstractmethod, abstractproperty
import logging
import urllib
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

    def __init__(self, update):
        self._message_dict = {
            "chat_id": None,
            "username": None,
            "command": None,
            "file_id": None,
            "text": None,
            "ignore": False,
        }
        self._original = update
        self._parse_update(update)
        # After the information is parsed, log the message!
        logger.info("New message: %s", self)

    def __str__(self):
        return json.dumps(self._message_dict)

    def _parse_command(self, text):
        """ Parse any msg starting with / """
        separate_command = text.split(" ", 1)
        # Remove the / from the command
        command = separate_command[0][1:]
        # Absorb the @ in case it is a directed command!
        if "@" in command:
            command = command.split("@")[0]
        # Check whether the command comes alone or has arguments
        if len(separate_command) == 1:
            text = ""
        else:
            text = separate_command[1]
        self._message_dict["command"] = command
        self._message_dict["text"] = text

    @abstractmethod
    def _parse_update(self, update):
        """ Parse the update and fill in _message_dict """
        return None

    @property
    def chat_id(self):
        """ Returns the chat id """
        return self._message_dict["chat_id"]

    @property
    def username(self):
        """ Returns the username """
        return self._message_dict["username"]

    @property
    def text(self):
        """ Returns the content of the message """
        return self._message_dict.get("text")

    @property
    def is_command(self):
        """ Returns true if the message is a command """
        return self._message_dict.get("command") is not None

    @property
    def command(self):
        """ Returns the command contained in the message """
        return self._message_dict.get("command")

    @property
    def is_file(self):
        """ Returns true if the message is a file """
        return self._message_dict.get("file_id") is not None

    @property
    def file_id(self):
        """ Returns the id of the file """
        return self._message_dict.get("file_id")

    @property
    def has_arguments(self):
        """ Returns true if the message is a command with arguments """
        return self.is_command and self.text is not None

    @property
    def ignore(self):
        """ Returns true if the message is to be ignored """
        return self._message_dict.get("ignore", False)

    @ignore.setter
    def ignore(self, val):
        self._message_dict["ignore"] = val


class Backend(ABC):
    """
    Main backend class for inheritting.

    It provides a number of base functions and wrappers

    The minimum set of methods and properties the backend must define are:

    _message_class: a reference to the Message class of the backend
    _get_updates: a method that should return a list of updates to act upon
    send_message: a method to communicate messages

    Others:
        - send_image
        - send_file
        - download_file

    """

    @abstractmethod
    def _get_updates(self, not_empty=False):
        """ Retrieve updates """

    @abstractmethod
    def send_message(self, text, chat):
        """ Sends a message to the chat """

    @abstractproperty
    def _message_class(self):
        pass

    def act_on_updates(self, action_function, not_empty=False):
        """
        Receive the input using _get_updates, parse it with
        the message class and act in consequence
        """
        all_updates = self._get_updates(not_empty=not_empty)
        for update in all_updates:
            msg = self._message_class(update)
            action_function(msg)

    def send_image(self, img_path, chat):
        """ Sends an image """
        logger.error("This backend does not implement sending images")

    def send_file(self, filepath, chat):
        """ Sends a file """
        logger.error("This backend does not implement sending files")

    def download_file(self, file_id, file_name):
        """Downloads a file using urllib.
        Understands file_id as the url
        """
        return urllib.request.urlretrieve(file_id, file_name)
