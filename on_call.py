from configurationData import chatId
from TelegramUtil import TelegramUtil

def run_command(args):

    teleAPI = TelegramUtil()
    if args.message:
        message_text = " ".join(args.message)
        teleAPI.send_message(message_text, chatId)
        print("Message sent")

    if args.file:
        teleAPI.send_file(args.file, chatId)

    if args.image:
        teleAPI.send_image(args.image, chatId)
        print("Image sent")
