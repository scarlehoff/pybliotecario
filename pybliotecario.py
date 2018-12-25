#!/usr/bin/env python3
from TelegramUtil import TelegramUtil
from core import main_loop
from configurationData import chatId

from argparse import ArgumentParser

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("message", help = "Message to send to Telegram", nargs = "*")
    parser.add_argument("-d", "--daemon", help = "Activate the librarian (default option)", action = "store_true", default = True)
    parser.add_argument("-i", "--image", help = "Send iamge to Telegram")
    return parser.parse_args()


if __name__ == "__main__":
    print("Initializing the pybliotecario")
    teleAPI = TelegramUtil()

    args = parse_args()

    if args.message:
        message_text = " ".join(args.message)
        teleAPI.send_message(message_text, chatId)
        print("Message sent")
    elif args.image:
        teleAPI.send_image(args.image, chatId)
        print("Image sent")
    else:
        print("Activating main loop")
        while True:
            main_loop(teleAPI)

        
