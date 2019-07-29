#!/usr/bin/env python3
import urllib
import requests
import json
import os.path

telegram_URL = "https://api.telegram.org/"

class TelegramUtil:
    """ This class handles all comunications with
    Telegram """

    def __init__(self, TOKEN, debug = False, timeout = 300):
        self.offset = None
        self.debug = debug
        self.timeout = timeout
        # Build app the API urls
        base_URL = telegram_URL + "bot{}/".format(TOKEN)
        self.base_fileURL = telegram_URL + "file/bot{}/".format(TOKEN)
        self.send_msg = base_URL + "sendMessage"
        self.send_img = base_URL + "sendPhoto"
        self.send_doc = base_URL + "sendDocument"
        self.get_msg = base_URL + "getUpdates"
        self.get_file = base_URL + "getFile"


    def __make_request(self, url):
        """ Returns the response for a given url
        In case of timeout, emulate an empty response
        """
        try:
            response = requests.get(url, timeout = self.timeout)
            content = response.content.decode("utf-8")
        except requests.exceptions.Timeout as e:
            content = '{ "ok": true, "result": [] }'
        return content

    def __get_json_from_url(self, url):
        """ Return the json response of a given url """
        content_response = self.__make_request(url)
        return json.loads(content_response)

    def __re_offset(self, updates):
        """ Updates the offset
        i.e., resets don't ask Telegram server for old messages
        """
        if len(updates) == 0:
            return
        li = []
        for update in updates:
            li.append(int(update["update_id"]))
        self.offset = max(li) + 1

    def get_filePath(self, fileId):
        """ Given a file id, retrieve the URI of the file
        in the remote server
        """
        url = self.get_file + "?file_id={0}".format(fileId)
        json = self.__get_json_from_url(url)
        # was it ok?
        if json['ok']:
            fpath = json['result']['file_path']
            return self.base_fileURL + fpath
        else:
            print(json['error_code'])
            print("Here's all the information we have on this request")
            print("This is the url we have used")
            print(url)
            return None

    def get_updates(self, not_empty = False):
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
            return self.get_updates(not_empty = True)
        if self.debug:
            print("Request url: {0}".format(url))
            print("Obtained updates: {0}".format(updates))
        try:
            result = updates["result"]
        except Exception as e:
            print("Error: ")
            print(str(e))
            print("List of updates: ") #Return an empty list and dont raise, let the program run
            print(updates)
            return []
        self.__re_offset(result)
        return result

    def send_message(self, text, chat):
        """ Send a message to a given chat """
        text = urllib.parse.quote_plus(text)
        url = self.send_msg + "?text={}&chat_id={}".format(text, chat)
        self.__make_request(url)

    def send_image(self, imgPath, chat):
        """ Send an image to a given chat """ 
        data = {'chat_id': chat}
        img = open(imgPath, 'rb')
        files = {'photo': ('picture.jpg', img)}  # Here, the ,"rb" thing
        blabla = requests.post(self.send_img, data=data, files=files)
        print(blabla.status_code, blabla.reason, blabla.content)

    def send_file(self, filePath, chat):
        data = {'chat_id': chat}
        file_stream = open(filePath, 'rb')
        doc_name = os.path.basename(filePath)
        files = {'document' : (doc_name, file_stream) }
        blabla = requests.post(self.send_doc, data=data, files=files)
        print(blabla.status_code, blabla.reason, blabla.content)

    def send_file_by_url(self, file_url, chat):
        """
        Sends a file using the telegram api which allows to send by url
        it only works for images/pdf, and not all pdfs
        """
        data = {'chat_id': chat,
                'document' : file_url}
        blabla = requests.post(self.send_doc, data=data)
        print(blabla.status_code, blabla.reason, blabla.content)

    def download_file(self, fileId, file_name_raw):
        """ Download file defined by fileId
        to given file_name """
        file_url = self.get_filePath(fileId)
        if not file_url:
            return None
        file_name = file_name_raw
        n = 0
        while os.path.isfile(file_name):
            filedir = os.path.dirname(file_name_raw)
            basename = os.path.basename(file_name_raw)
            file_name = "{0}/n{1}-{2}".format(filedir, n, basename)
            n += 1
        return urllib.request.urlretrieve(file_url, file_name)


if __name__ == "__main__":
    print("Testing TelegramUtil")
    ut = TelegramUtil(debug = True)
    results = ut.get_updates()
    for result in results:
        print("Complete json:")
        print(result)
        message = result['message']
        chat_id = message['chat']['id']
        txt = message['text']
        print("Message from {0}: {1}".format(chat_id, txt))
        ut.send_message("Message received", chat_id)
    ut.timeout = 1
    ut.get_updates() # Use the offset to confirm updates

