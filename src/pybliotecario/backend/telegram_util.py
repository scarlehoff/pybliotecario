#!/usr/bin/env python3
"""
    Telegram backend
"""

import json
import logging
from time import sleep
import urllib

import requests

from pybliotecario.backend.basic_backend import Backend, Message

TELEGRAM_URL = "https://api.telegram.org/"

logger = logging.getLogger(__name__)

# Keys included in telegram chats that basically are telling you to ignore it
IGNOREKEYS = {"new_chat_participant", "left_chat_participant", "sticker", "game", "contact"}


def log_request(status_code, reason, content):
    """Log the status of the send requests"""
    result = f"Request sent, status code: {status_code} - {reason}: {content}"
    logger.info(result)


class TelegramMessage(Message):
    """Telegram implementation of the Message class"""

    _type = "Telegram"
    _group_info = None

    def _parse_update(self, update):
        """Receives an update in the form of a dictionary (that came from a json)
        and fills the message attributes
        """
        keys = update.keys()
        # First check whether this is a message, edited message or a channel post
        msg_types = ["message", "edited_message", "edited_channel_post"]
        msg = None
        for msg_type in msg_types:
            if msg_type in keys:
                msg = msg_type
        if msg is None:
            logger.warning(f"Message not in {msg_types}, ignoring")
            logger.warning(update)
            self.ignore = True
            return
        message = update[msg]
        # Get the keys of the message (and check whether it should be ignored)
        msg_keys = message.keys()
        if set(msg_keys) & IGNOREKEYS:
            self.ignore = True
            return
        # Now get the chat data and id
        chat_data = message["chat"]
        self._chat_id = chat_data["id"]
        # I believe from and chat_data are only different when using a group
        # but the pybliotecario has not really been tested (or used) in groups...
        from_data = message.get("from", chat_data)

        # Populate the user (in the list, last has more priority)
        username = "unknown_user"
        for user_naming in ["last_name", "first_name", "username"]:
            username = from_data.get(user_naming, username)
        self._username = username

        # Check the filetype
        text = None
        if "photo" in message:
            # If it is a photo, get the file id and use the caption as the title
            photo_data = message["photo"][-1]
            self._file_id = photo_data["file_id"]
            text = message.get("caption", "untitled")
        elif "document" in message:
            # If it is a document, telegram gives you everything you need
            file_dict = message["document"]
            self._file_id = file_dict["file_id"]
            text = message.get("caption", None)
            if text is None:
                # Use the file name
                text = file_dict["file_name"]
        else:
            # Normal text message
            text = message.get("text", "")

        # In Telegram we can also have groups
        if "group" in chat_data:
            self._group_info = chat_data

        # Finally, with the piece of text left, parse the possible command
        # _parse_command will fill both text and command
        self._parse_command(text)

    @property
    def is_group(self):
        """Returns true if the message was from a group"""
        return self._group_info is not None


class TelegramUtil(Backend):
    """This class handles all communications with
    Telegram"""

    _message_class = TelegramMessage

    def __init__(self, config=None, token=None, timeout=300, **kwargs):
        super().__init__(config, **kwargs)
        if token is None:
            if config is None:
                raise ValueError("Either a config or a token must be provided for Telegram")
            token = config.defaults().get("token")

        self.offset = None
        self.timeout = timeout
        # Build app the API urls
        base_URL = TELEGRAM_URL + f"bot{token}/"
        self.base_fileURL = TELEGRAM_URL + f"file/bot{token}/"
        self.send_msg = base_URL + "sendMessage"
        self.send_img = base_URL + "sendPhoto"
        self.send_doc = base_URL + "sendDocument"
        self.get_msg = base_URL + "getUpdates"
        self.get_file = base_URL + "getFile"

    def __make_request(self, url):
        """Returns the response for a given url
        In case of timeout, emulate an empty response
        """
        content = '{ "ok": true, "result": [] }'
        try:
            response = requests.get(url, timeout=self.timeout)
            content = response.content.decode("utf-8")
        except requests.exceptions.Timeout:
            logger.warning("Timeout. Sleeping for 2 minutes...")
            # After a timeout, sleep for 1 minute
            sleep(60)
        except requests.exceptions.ConnectionError as e:
            logger.error(e)
        return content

    def __get_json_from_url(self, url):
        """Return the json response of a given url"""
        content_response = self.__make_request(url)
        res_json = json.loads(content_response)
        return res_json

    def __re_offset(self, updates):
        """Updates the offset
        i.e., resets don't ask Telegram server for old messages
        """
        if not updates:  # len(updates) == 0
            return
        li = []
        for update in updates:
            li.append(int(update["update_id"]))
        self.offset = max(li) + 1

    def _get_filepath(self, file_id):
        """Given a file id, retrieve the URI of the file
        in the remote server
        """
        url = self.get_file + f"?file_id={file_id}"
        jsonret = self.__get_json_from_url(url)
        # was it ok?
        if jsonret["ok"]:
            fpath = jsonret["result"]["file_path"]
            return self.base_fileURL + fpath
        else:
            logger.info(jsonret["error_code"])
            logger.info("Here's all the information we have on this request")
            logger.info("This is the url we have used")
            logger.info(url)
            return None

    def _get_updates(self, not_empty=False):
        """
        Returns a json with the last messages the bot has received
        when an offset is found, previous msg are not retrieved
        We use longpolling to keep the connection open for timeout seconds

        If not_empty = True, this function will only return when a message arrives
        """
        url = f"{self.get_msg}?timeout={self.timeout}"
        if self.offset:
            url += f"&offset={self.offset}"
        updates = self.__get_json_from_url(url)

        if not updates and not_empty:
            return self._get_updates(not_empty=True)

        if self._debug:
            logger.info("Request url: %s", url)
            logger.info("Obtained updates: %s", updates)

        try:
            result = updates["result"]
        except Exception as e:
            # in case of ANY exception, just logger.info it out and let the program run
            logger.error("Error: ")
            logger.error(str(e))
            logger.error("List of updates: ")
            logger.error(updates)
            return []

        self.__re_offset(result)
        return result

    def send_message(self, text, chat, markdown=False, **kwargs):
        """Send a message to a given chat"""
        text = urllib.parse.quote_plus(text)
        url = f"{self.send_msg}?text={text}&chat_id={chat}"
        if markdown:
            url += "&parse_mode=markdown"
        content = self.__make_request(url)
        # Sometimes, when using markdown, the update might fail
        if markdown and not json.loads(content).get("ok"):
            # If that's the case, try to resend without md
            self.send_message(text, chat, **kwargs)

    def send_image(self, img_path, chat):
        """Send an image to a given chat"""
        data = {"chat_id": chat}
        with open(img_path, "rb") as img:
            files = {"photo": ("picture.jpg", img)}  # Here, the "rb" thing
            blabla = requests.post(self.send_img, data=data, files=files)
        log_request(blabla.status_code, blabla.reason, blabla.content)

    def send_file(self, filepath, chat):
        data = {"chat_id": chat}
        files = {"document": (filepath.name, filepath.open("rb"))}
        blabla = requests.post(self.send_doc, data=data, files=files)
        log_request(blabla.status_code, blabla.reason, blabla.content)

    def send_file_by_url(self, file_url, chat):
        """
        Sends a file using the telegram api which allows to send by url
        it only works for images/pdf, and not all pdfs
        """
        data = {"chat_id": chat, "document": file_url}
        blabla = requests.post(self.send_doc, data=data)
        logger.info(blabla.status_code, blabla.reason, blabla.content)

    def download_file(self, file_id, file_path):
        """Download file defined by file_id to given file_path"""
        file_url = self._get_filepath(file_id)
        if not file_url:
            return None
        n = 0
        # If the file already exists, iterate it by adding a nX
        while file_path.exists():
            new_name = f"n{n}-{file_path.name}"
            file_path = file_path.parent / new_name
            n += 1
        return urllib.request.urlretrieve(file_url, file_path)


if __name__ == "__main__":
    logger.info("Testing TelegramUtil")
    token = "must put a token here to test"
    ut = TelegramUtil(token=token, debug=True)
    # noinspection PyProtectedMember
    results = ut._get_updates()
    for res in results:
        logger.info("Complete json:")
        logger.info(res)
        msg_example = res["message"]
        chat_id = msg_example["chat"]["id"]
        txt = msg_example["text"]
        logger.info("Message from %s: %s", chat_id, txt)
        ut.send_message("Message received", chat_id)
    ut.timeout = 1
    # noinspection PyProtectedMember
    ut._get_updates()  # Use the offset to confirm updates
