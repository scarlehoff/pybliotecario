"""
    Mock backend in order to test the pybliotecario
    without communication with any service
"""

import pathlib
from datetime import datetime
import numpy as np

from pybliotecario.backend.telegram_util import TelegramMessage

TESTID = 1234  # chat id for the test backend
_TESTUSER = "hiro"


class TestMessage(TelegramMessage):
    """ Copy of the TelegramMessage class """

    _type = "Test"


def _create_fake_msg(text):
    ret = {
        "update_id": np.random.randint(1000),
        "message": {
            "message_id": np.random.randint(1000),
            "from": {
                "id": TESTID,
                "is_bot": False,
                "first_name": _TESTUSER,
                "last_name": _TESTUSER,
                "username": _TESTUSER,
                "language_code": "en",
            },
            "chat": {
                "id": TESTID,
                "first_name": _TESTUSER,
                "last_name": _TESTUSER,
                "username": _TESTUSER,
                "type": "private",
            },
            "date": datetime.now().toordinal(),
            "text": text,
        },
    }
    return ret


class TestUtil:
    """
    The test utility tries to behave as other backend would

    It provides _get_updates / send_message just as any other backend
    but it writes/reads the update from a communication file.

    If fake_msgs are given, it will read the messages from those instead
    of from the communication_file
    Likewise, if a communication_file is not given, it will return the message
    instead of writting it down

    Parameters
    ----------
        communication_file: str/pathlib
            file to write/read from
        fake_msg: list(str)
            list of messages to generate
    """

    def __init__(self, communication_file=None, fake_msgs=None, **kwargs):
        if communication_file is None:
            self.comm_file = False
        else:
            self.comm_file = pathlib.Path(communication_file)
        self.fake_msgs = fake_msgs

    def _get_updates(self, not_empty=False):
        """
        Returns a json with the latest messages the bot has received

        This test function creates a list of two mock messages which
        will be in turn parsed by the Message class
        """
        if self.fake_msgs is not None:
            msgs = self.fake_msgs
        elif self.comm_file:
            msgs = self.comm_file.read_text().split("\n")
        else:
            msgs = ["This is onyl a test", "Another one"]
        return [_create_fake_msg(i) for i in msgs]

    def act_on_updates(self, action_function, not_empty=False):
        """
        Receive the input using _get_updates, parse it with
        the telegram message class and act in consequence
        """
        all_updates = self._get_updates(not_empty=not_empty)
        for update in all_updates:
            msg = TestMessage(update)
            action_function(msg)

    def send_message(self, text, chat):
        """
        Sends a message to the communication_file this class has been
        instantiated with
        """
        if self.comm_file:
            with open(self.comm_file, "a") as f:
                f.write(f"{text}\n")
            return None
        return text

    def send_image(self, *args):
        """ Writes the img_path to the comm file """
        return self.send_message(*args)

    def send_file(self, *args):
        """ Writes the file_path to the comm file """
        return self.send_message(*args)

    # Auxiliary
    def is_msg_in_file(self, msg):
        """Check whether the given message is in the comms file
        This is something that is only useful for the TestUtil backend"""
        read_text = self.comm_file.read_text()
        return msg in read_text
