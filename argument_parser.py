from argparse import ArgumentParser

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("message", help = "Message to send to Telegram", nargs = "*")
    parser.add_argument("-d", "--daemon", help = "Activate the librarian", action = "store_true")
    parser.add_argument("-i", "--image", help = "Send iamge to Telegram")
    parser.add_argument("-f", "--file", help = "Send file to Telegram")
    return parser.parse_args()


