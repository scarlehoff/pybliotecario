#!/usr/bin/env python3
"""
    Facebook backend

    Using this backend will stat a flask server in the selected port.
    Testing this backend is a bit of a pain as one has to be in a server
    which facebook should be able to access with a valid SSL certificate.

    For quick testing, I am using hthe following setup:
    ~$ iptables -A INPUT -p tcp --dport 3000  -j ACCEPT
    ~$ ngrok http <my_personal_server>:3000

    And then I open the flask server in the port 3000 and give facebook
    the ngrok url.
    For actual deployment one would want to set up some actual server.
"""

import json
import pathlib
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
        print(update)
        msg_info = update["entry"][0]["messaging"][0]
        # Check who sent it
        sender_id = msg_info["sender"]["id"]
        self._message_dict["chat_id"] = sender_id
        # Get the msg
        msg = msg_info["message"]
        # get the text and parse it if necessary
        text = msg.get("text")
        self._message_dict["text"] = text
        if text and text.startswith("/"):
            self._parse_command(text)
        # In facebook we have either text or image
        # TODO: in facebook you can pass more than one img at once...
        attachment = msg.get("attachments")
        if attachment is not None:
            at_info = attachment[0]
            # Checked for images and files and seems to work
            url = at_info["payload"]["url"]
            self._message_dict["file_id"] = url
            self._message_dict["text"] = url.split("?")[0].split("/")[-1]


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
        self.auth = {"access_token": self.page_access_token}

    def validate_hook(self):
        """Facebook needs to validate the webhook
        This is a small utility to do so
        """

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
        payload = {"message": {"text": text}, "recipient": {"id": chat}}
        response = requests.post(FB_API, params=self.auth, json=payload)
        return response.json()

    def send_data(self, payload):
        """Sends data to facebook messenger.
        This method uses MultipartEncoder: https://toolbelt.readthedocs.io/
        to stream multipart form-data
        """
        try:
            from requests_toolbelt import MultipartEncoder
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                "Install 'requests-toolbelt' to send images and files to facebook"
            ) from e

        encoded_payload = MultipartEncoder(payload)
        header = {"Content-Type": encoded_payload.content_type}
        response = requests.post(FB_API, params=self.auth, data=encoded_payload, headers=header)
        return response.json()

    def send_image(self, img_path, chat):
        """Sends an image to facebook
        Basically the requests form of the curl command here:
        https://developers.facebook.com/docs/messenger-platform/send-messages#url
        """
        img = pathlib.Path(img_path)
        payload = {
            "recipient": json.dumps({"id": chat}),
            "message": json.dumps(
                {
                    "attachment": {
                        "type": "image",
                        "payload": {"is_reusable": True},
                    }
                }
            ),
            "filedata": (img.stem, img.read_bytes(), f"image/{img.suffix[1:]}"),
        }
        return self.send_data(payload)

    def send_file(self, filepath, chat):
        """ Sends a file to fb, similar to send_image """
        fff = pathlib.Path(filepath)
        payload = {
            "recipient": json.dumps({"id": chat}),
            "message": json.dumps(
                {
                    "attachment": {
                        "type": "file",
                        "payload": {"is_reusable": True},
                    }
                }
            ),
            "filedata": (fff.name, fff.read_bytes()),
        }
        return self.send_data(payload)


if __name__ == "__main__":
    logger.info("Testing FB Util")
    verify = "your_verify_token"
    app_token = "your_app_key"
    fb_util = FacebookUtil(app_token, verify, debug=True)
    fb_util.act_on_updates(lambda x: print(x))
