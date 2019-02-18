from argparse import ArgumentParser

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("message", help = "Message to send to Telegram", nargs = "*")
    parser.add_argument("-d", "--daemon", help = "Activate the librarian", action = "store_true")
    parser.add_argument("-i", "--image", help = "Send iamge to Telegram")
    parser.add_argument("-f", "--file", help = "Send file to Telegram")
    parser.add_argument("--arxiv_new", help = "Send a msg containing a digest of the new submissions to arxiv", action = "store_true")
    parser.add_argument("--weather", help = "Sends a msg to telegram with the current weather and a small forecast", action = "store_true")
    return parser.parse_args()


