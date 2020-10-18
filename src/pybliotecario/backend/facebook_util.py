#!/usr/bin/env python3
"""
    Facebook backend

    Using this backend will stat a flask server in the selected port
"""

import logging
import requests
from pybliotecario.backend.basic_backend import Message, Backend

_HAS_FLASK = True
try:
    from flask import Flask, request
except ModuleNotFoundError:
    _HAS_FLASK = False


logger = logging.getLogger(__name__)

FB_API = "https://graph.facebook.com/v2.12/me/messages"


def log_request(status_code, reason, content):
    """ Log the status of the send requests """
    result = "Request sent, status code: {0} - {1}: {2}".format(status_code, reason, content)
    logger.info(result)


class FacebookMessage(Message):
    """ Facebook implementation of the Message class """

    _type = "facebook"
    _group_info = None

    def _parse_update(self, update):
        """Receives an update in the form of a dictionary (that came from a json)
        and fills in the _message_dict dictionary
        """
        # Check whether it is the correct object, otherwise out
        if update.get("object") != "page":
            logger.warning("Message not a object: page, ignoring")
            logger.warning(update)
            self.ignore = True
            return
        msg = update["entry"][0]["messaging"][0]
        # Check who sent it
        sender_id = msg["sender"]["id"]
        self._message_dict["chat_id"] = sender_id
        # Get the text
        text = msg["message"]["text"]
        # and parse it if necessary
        self._message_dict["text"] = text
        if text and text.startswith("/"):
            self._parse_command(text)


class FacebookUtil(Backend):
    """This class handles all comunications with
    Telegram"""

    _message_class = FacebookMessage

    def __init__(self, PAGE_TOKEN, VERIFY_TOKEN, host="0.0.0.0", port=3000, debug=False):
        if not _HAS_FLASK:
            # Do the error now
            raise ModuleNotFoundError("No module named 'flask'")

        self.page_access_token = PAGE_TOKEN
        self.verify_token = VERIFY_TOKEN
        self.port = port
        self.host = host
        app = Flask(__name__)
        # Load the listener into the webhook endpoint
        app.add_url_rule("/webhook", "webhook", self.listener, methods=["POST", "GET"])
        self.flask_app = app
        self.debug = debug
        self.action_function = None

    def listener(self):
        """ Main function flask will use to listen at the webhook endpoint """
        if request.method == "GET":
            if request.args.get("hub.verify_token") == self.verify_token:
                return request.args.get("hub.challenge")
            else:
                return "incorrect"

        if request.method == "POST":
            msg = self._message_class(request.json)
            self.action_function(msg)
            logger.info(msg)
            # After we have finished return a 200 Ok
            return "All ok"

    def act_on_updates(self, action_function, not_empty=False):
        """Sets the action function to be used by the listener and then
        opens the webhook to wait ofr updates and act on them
        """
        self.action_function = action_function
        self.flask_app.run(host=self.host, port=self.port, debug=self.debug)

    def _get_updates(self, not_empty=False):
        """ This class skips get_updates and uses act_on_updates directly """
        pass

    def send_message(self, text, chat):
        """ Sends a message response to facebook """
        payload = {
            "message": {"text": text},
            "recipient": {"id": chat},
            "notification_type": "regular",
        }
        auth = {"access_token": self.page_access_token}
        response = requests.post(FB_API, params=auth, json=payload)
        return response.json()


if __name__ == "__main__":
    logger.info("Testing FB Util")
    verify = "your_verify_token"
    app_token = "your_app_key"
    fb_util = FacebookUtil(app_token, verify, debug=True)
    fb_util.act_on_updates(lambda x: print(x))
