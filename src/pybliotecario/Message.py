###### Esta clase tiene que ser redefinida de forma uqe definamos un MessageParser con una serie de opciones y un Message
###### donde el message parser es algo en plan que define una serie de opciones y el message pues tiene todos los getters


registeredCommands = []

class Message:
    # Variables that we are going to parse from json:
    # chat_id              - Id of the chat the message came from
    # username            - user who sent the message
    # is_command           - t/f
    # isRegisteredCommand - t/f
    # isGroup             - t/f
    # isFile              - t/f
    # fileId              - file id
    # text                - actual content of the message (minus /command)
    # command             - command given in /command (or "")
    # ignore              - t/f (whether this message should be ignored)

    def __init__(self, jsonDict):
        # ignore keys:
        ign_keys = ["new_chat_participant",
                "left_chat_participant"]
        msg = "message"
        self.json = jsonDict
        keys = jsonDict.keys()
        if msg not in keys:
            if "edited_message" in keys:
                msg = 'edited_message'
            elif "edited_channel_post" in keys:
                msg = "edited_channel_post"
        try:
            message = jsonDict[msg]
        except:
            print("   >>>>> ")
            print(jsonDict)
            raise Exception("Not a message or an edited message?")
        msgKeys = message.keys()
        if set(ign_keys) & set(msgKeys):
            self.ignore = True
            return
        else:
            self.ignore = False
        chatData = message['chat']
        if 'from' in message.keys():
            fromData = message['from']
        else:
            fromData = chatData # something has changed or was this a special type of msg???
        # Populate general fields
        self.username = fromData['username']
        self.chat_id = chatData['id']

        # Check the filetyp of what we just received
        if "photo" in msgKeys:
            self.isFile = True
            photoData = message["photo"][-1]
            self.fileId = photoData["file_id"]
            if "caption" in msgKeys:
                self.text = message["caption"]
            else:
                self.text = "untitled"
            if not self.text.endswith( (".jpg", ".JPG", ".png", ".PNG") ):
                self.text += ".jpg"
        elif "document" in msgKeys:
            self.isFile = True
            fileData = message["document"]
            self.fileId = fileData["file_id"]
            self.text = fileData["file_name"]
        else:
            self.text = message["text"]
            self.isFile = False

        # Check whether the msg comes from a group
        self.isGroup = chatData['type'] is 'group'

        # Now check whether the msg has the structure of a command
        if self.text[0] == '/':
            self.is_command = True
        else:
            self.is_command = False
            self.command = ""
            self.isRegisteredCommand = False

        if self.is_command:
            allText = self.text.split(' ', 1)
            self.command = allText[0][1:]
            # Absorb the @ in case is it a directed command
            if '@' in self.command:
                self.command = self.command.split('@')[0]
            self.text = allText[-1]
            self.isRegisteredCommand = self.command in registeredCommands
        