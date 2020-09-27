"""
    Mock backend in order to test the pybliotecario
    without communication with any service
"""

import copy
import numpy as np
from datetime import datetime

from pybliotecario.Message import Message

_TESTID = 1234  # chat id for the test backend
_TESTUSER = "hiro"


def _create_fake_msg(text):
    ret = {
        "update_id": np.random.randint(1000),
        "message": {
            "message_id": np.random.randint(1000),
            "from": {
                "id": _TESTID,
                "is_bot": False,
                "first_name": _TESTUSER,
                "last_name": _TESTUSER,
                "username": _TESTUSER,
                "language_code": "en",
            },
            "chat": {
                "id": _TESTID,
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
    """"""

    def __init__(self, communication_file, fake_msgs=None, debug=True, timeout=None):
        self.debug = debug
        self.comm_file = communication_file
        self.fake_msgs = fake_msgs

    def get_updates(self, not_empty=False):
        """
        Returns a json with the latest messages the bot has received

        This test function creates a list of two mock messages which
        will be in turn parsed by the Message class
        """
        if self.fake_msgs is None:
            msgs = ["This is onyl a test", "Another one"]
        else:
            msgs = self.fake_msgs
        return [_create_fake_msg(i) for i in msgs]

    def send_message(self, text, chat):
        """
        Sends a message to the communication_file this class has been
        instantiated with
        """
        with open(self.comm_file, "w") as f:
            f.write(text)

    def send_image(self, *args):
        """ Writes the img_path to the comm file """
        return self.send_message(*args)

    def send_file(self, *args):
        """ Writes the file_path to the comm file """
        return self.send_message(*args)


if __name__ == "__main__":
    cls = TestUtil("/tmp/test.txt")
    res = cls.get_updates()
    msgs = [Message(i) for i in res]
