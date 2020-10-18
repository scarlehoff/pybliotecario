"""
    Telegram backend
"""

#!/usr/bin/env python3
import json
import os.path
import urllib
import logging
import requests
from pybliotecario.backend.basic_backend import Message, Backend

TELEGRAM_URL = "https://api.telegram.org/"

logger = logging.getLogger(__name__)

# Keys included in telegram chats that basically are telling you to ignore it
IGNOREKEYS = set(["new_chat_participant", "left_chat_participant", "sticker", "game", "contact"])


def log_request(status_code, reason, content):
    """ Log the status of the send requests """
    result = "Request sent, status code: {0} - {1}: {2}".format(status_code, reason, content)
    logger.info(result)


class TelegramMessage(Message):
    """ Telegram implementation of the Message class """

    _type = "Telegram"
    _group_info = None

    def _parse_update(self, update):
        """Receives an update in the form of a dictionary (that came from a json)
        and fills in the _message_dict dictionary
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
        self._message_dict["chat_id"] = chat_data["id"]
        # TODO test this part of the parser as this 'from' was a legacy thing at some point
        from_data = message.get("from", chat_data)

        # Populate the user (in the list, last has more priority)
        username = "unknown_user"
        for user_naming in ["last_name", "first_name", "username"]:
            username = from_data.get(user_naming, username)
        self._message_dict["username"] = username

        # Check the filetype
        text = None
        if "photo" in message:
            # If it is a photo, get the file id and use the caption as the title
            photo_data = message["photo"][-1]
            self._message_dict["file_id"] = photo_data["file_id"]
            text = message.get("caption", "untitled")
            if not text.endswith((".jpg", ".JPG", ".png", ".PNG")):
                text += ".jpg"
        elif "document" in message:
            # If it is a document, teleram gives you everything you need
            file_dict = message["document"]
            self._message_dict["file_id"] = file_dict["file_id"]
            text = file_dict["file_name"]
        else:
            # Normal text message
            text = message.get("text", "")

        # In Telegram we can also have groups
        if "group" in chat_data:
            self._group_info = chat_data

        # Finally check whether the message looks like a command
        self._message_dict["text"] = text
        if text and text.startswith("/"):
            self._parse_command(text)

    @property
    def is_group(self):
        """ Returns true if the message was from a group """
        return self._group_info is not None


class TelegramUtil(Backend):
    """This class handles all comunications with
    Telegram"""

    _message_class = TelegramMessage

    def __init__(self, TOKEN, debug=False, timeout=300):
        self.offset = None
        self.debug = debug
        self.timeout = timeout
        # Build app the API urls
        base_URL = TELEGRAM_URL + "bot{}/".format(TOKEN)
        self.base_fileURL = TELEGRAM_URL + "file/bot{}/".format(TOKEN)
        self.send_msg = base_URL + "sendMessage"
        self.send_img = base_URL + "sendPhoto"
        self.send_doc = base_URL + "sendDocument"
        self.get_msg = base_URL + "getUpdates"
        self.get_file = base_URL + "getFile"

    def __make_request(self, url):
        """Returns the response for a given url
        In case of timeout, emulate an empty response
        """
        try:
            response = requests.get(url, timeout=self.timeout)
            content = response.content.decode("utf-8")
        except requests.exceptions.Timeout:
            content = '{ "ok": true, "result": [] }'
        return content

    def __get_json_from_url(self, url):
        """ Return the json response of a given url """
        content_response = self.__make_request(url)
        return json.loads(content_response)

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
        url = self.get_file + "?file_id={0}".format(file_id)
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
        url = "{0}?timeout={1}".format(self.get_msg, self.timeout)
        if self.offset:
            url += "&offset={0}".format(self.offset)
        updates = self.__get_json_from_url(url)
        if not updates and not_empty:
            return self._get_updates(not_empty=True)
        if self.debug:
            logger.info("Request url: {0}".format(url))
            logger.info("Obtained updates: {0}".format(updates))
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

    def send_message(self, text, chat):
        """ Send a message to a given chat """
        text = urllib.parse.quote_plus(text)
        url = self.send_msg + "?text={}&chat_id={}".format(text, chat)
        self.__make_request(url)

    def send_image(self, img_path, chat):
        """ Send an image to a given chat """
        data = {"chat_id": chat}
        img = open(img_path, "rb")
        files = {"photo": ("picture.jpg", img)}  # Here, the ,"rb" thing
        blabla = requests.post(self.send_img, data=data, files=files)
        log_request(blabla.status_code, blabla.reason, blabla.content)

    def send_file(self, filepath, chat):
        data = {"chat_id": chat}
        file_stream = open(filepath, "rb")
        doc_name = os.path.basename(filepath)
        files = {"document": (doc_name, file_stream)}
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

    def download_file(self, file_id, file_name):
        """Download file defined by file_id
        to given file_name"""
        file_url = self._get_filepath(file_id)
        if not file_url:
            return None
        n = 0
        while os.path.isfile(file_name):
            filedir = os.path.dirname(file_name)
            basename = os.path.basename(file_name)
            file_name = "{0}/n{1}-{2}".format(filedir, n, basename)
            n += 1
        return urllib.request.urlretrieve(file_url, file_name)


if __name__ == "__main__":
    logger.info("Testing TelegramUtil")
    token = "must put a token here to test"
    ut = TelegramUtil(token, debug=True)
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
    ut._get_updates()  # Use the offset to confirm updates
