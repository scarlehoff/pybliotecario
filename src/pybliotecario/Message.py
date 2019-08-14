###### Esta clase tiene que ser redefinida de forma uqe definamos un MessageParser con una serie de opciones y un Message
###### donde el message parser es algo en plan que define una serie de opciones y el message pues tiene todos los getters


registeredCommands = []
import logging

log = logging.getLogger(__name__)


class Message:
    # Variables that we are going to parse from json:
    # chat_id              - Id of the chat the message came from
    # username            - user who sent the message
    # is_command           - t/f
    # isRegisteredCommand - t/f
    # has_arguments       - t/f
    # is_group             - t/f
    # isFile              - t/f
    # fileId              - file id
    # text                - actual content of the message (minus /command)
    # command             - command given in /command (or "")
    # ignore              - t/f (whether this message should be ignored)

    def __init__(self, jsonDict):
        # ignore keys:
        ign_keys = ["new_chat_participant", "left_chat_participant", "sticker"]
        msg = "message"
        self.json = jsonDict
        keys = jsonDict.keys()
        if msg not in keys:
            if "edited_message" in keys:
                msg = "edited_message"
            elif "edited_channel_post" in keys:
                msg = "edited_channel_post"
        try:
            message = jsonDict[msg]
        except:
            log.info("   >>>>> ")
            log.info(jsonDict)
            raise Exception("Not a message or an edited message?")
        msgKeys = message.keys()
        if set(ign_keys) & set(msgKeys):
            self.ignore = True
            return
        else:
            self.ignore = False
        self.has_arguments = False
        chatData = message["chat"]
        if "from" in message.keys():
            fromData = message["from"]
        else:
            fromData = chatData  # something has changed or was this a special type of msg???
        # Populate general fields
        # Check whetehr username exists, otherwise use name, otherwise, unknown
        if "username" in fromData:
            self.username = fromData["username"]
        elif "first_name" in fromData:
            self.username = fromData["first_name"]
        elif "last_name" in fromData:
            self.username = fromData["last_name"]
        else:
            self.username = "unknown_user"
        self.chat_id = chatData["id"]

        # Check the filetyp of what we just received
        if "photo" in msgKeys:
            self.isFile = True
            photoData = message["photo"][-1]
            self.fileId = photoData["file_id"]
            if "caption" in msgKeys:
                self.text = message["caption"]
            else:
                self.text = "untitled"
            if not self.text.endswith((".jpg", ".JPG", ".png", ".PNG")):
                self.text += ".jpg"
        elif "document" in msgKeys:
            self.isFile = True
            fileData = message["document"]
            self.fileId = fileData["file_id"]
            self.text = fileData["file_name"]
        elif "sticker" in msgKeys:
            self.isSticker = True
            stickerData = message["sticker"]
            self.stickerSet = stickerData["set_name"]
        else:
            self.text = message.get("text")
            self.isFile = False

        # Check whether the msg comes from a group
        self.is_group = chatData["type"] is "group"

        #  Now check whether the msg has the structure of a command
        if self.text[0] == "/":
            self.is_command = True
        else:
            self.is_command = False
            self.command = ""
            self.isRegisteredCommand = False

        if self.is_command:
            all_text = self.text.split(" ", 1)
            # Check whether the command comes by itself or has arguments
            if len(all_text) > 1:
                self.has_arguments = True
            # Remove the /
            self.command = all_text[0][1:]
            # Absorb the @ in case is it a directed command
            if "@" in self.command:
                self.command = self.command.split("@")[0]
            self.text = all_text[-1]
            self.isRegisteredCommand = self.command in registeredCommands
