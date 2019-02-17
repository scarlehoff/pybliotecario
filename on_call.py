from configurationData import chatId
from TelegramUtil import TelegramUtil
import pdb


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

    if args.arxiv_new:
        from components import arxiv_recent_filtered
        from configurationData import arxiv_filter_dict, arxiv_categories
        msg = arxiv_recent_filtered(arxiv_categories, arxiv_filter_dict)
        teleAPI.send_message(msg, chatId)
        print("Arxiv information sent")
