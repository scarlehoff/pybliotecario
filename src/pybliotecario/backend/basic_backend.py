"""
    Base/abstract backend classes:

    - Message
    - Backend

    Each backend should implement its own message type and inherit from backend
"""

from abc import ABC, abstractmethod
import logging
import urllib
import json

logger = logging.getLogger(__name__)


class Message(ABC):
    """
    Base message class

    Any implementation of the message should read the incoming update
    and save the following information in the appropiate attributes:
     - chat id
     - username of the sender
     - text of the msg
     - command (if any)
     - file id (if any)
     - ignore (if the msg is to be ignored)
    through the ``_parse_update`` method.
    """

    _type = "Abstract"
    _original = None

    def __init__(self, update):
        self._chat_id = None
        self._username = None
        self._command = None
        self._file_id = None
        self._text = None
        self._ignore = False
        self._raw = None
        self._original = update
        self._parse_update(update)
        # After the information is parsed, log the message!
        logger.info("New message: %s", self)

    def __str__(self):
        rep = ["chat_id", "username", "command", "file_id", "text", "ignore"]
        msg_dict = {}
        for r in rep:
            msg_dict[r] = getattr(self, r)
        return json.dumps(msg_dict)

    def _parse_command(self, text):
        """Separate messages containing commands into the command and text attributes
        a command is a message which starts with /"""
        if not text.startswith("/"):
            self._command = None
            self._text = text
            return
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
        self._command = command
        self._text = text

    @abstractmethod
    def _parse_update(self, update):
        """Parse the update and fill in all entries"""
        return None

    @property
    def raw(self):
        """Return the raw message, understood as command + text"""
        original = ""
        if self.is_command:
            original += f"/{self.command}"
        if self.text is not None:
            original += self.text
        if self.is_file:
            original += " (contains file)"
        return original

    @property
    def chat_id(self):
        """Returns the chat id"""
        return self._chat_id

    @property
    def username(self):
        """Returns the username"""
        return self._username

    @property
    def text(self):
        """Returns the content of the message"""
        return self._text

    @property
    def is_command(self):
        """Returns true if the message is a command"""
        return self.command is not None

    @property
    def command(self):
        """Returns the command contained in the message"""
        return self._command

    @property
    def is_file(self):
        """Returns true if the message is a file"""
        return self.file_id is not None

    @property
    def file_id(self):
        """Returns the id of the file"""
        return self._file_id

    @property
    def has_arguments(self):
        """Returns true if the message is a command with arguments"""
        return self.is_command and self.text is not None

    @property
    def ignore(self):
        """Returns true if the message is to be ignored"""
        return self._ignore

    @ignore.setter
    def ignore(self, val):
        self._ignore = val


class Backend(ABC):
    """
    Main backend class for inheriting.

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

    _max_size = 99999

    @abstractmethod
    def _get_updates(self, not_empty=False):
        """Retrieve updates"""

    def raw_updates(self):
        """Returns a raw version of the updates as implemented by the child class"""
        return self._get_updates(not_empty=True)

    @abstractmethod
    def send_message(self, text, chat, **kwargs):
        """Sends a message to the chat"""

    @property
    @abstractmethod
    def _message_class(self):
        pass

    def _break_msg(self, msg):
        """Find the position of the closest whitespace to size in order to break a given msg
        It prioritizes newlines, then spaces, then just returns size
        (but only from half the msg onwards)
        """
        if len(msg) < self._max_size:
            return self._max_size
        available_msg = msg[: self._max_size]
        for break_char in ["\n", " "]:
            last_break = available_msg.rindex(break_char)
            if last_break > int(self._max_size / 2):
                return last_break
        return self._max_size

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
        """Sends an image"""
        logger.error("This backend does not implement sending images")

    def send_file(self, filepath, chat):
        """Sends a file"""
        logger.error("This backend does not implement sending files")

    def download_file(self, file_id, file_name):
        """Downloads a file using urllib.
        Understands file_id as the url
        """
        return urllib.request.urlretrieve(file_id, file_name)
