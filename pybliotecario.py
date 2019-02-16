#!/usr/bin/env python3
from TelegramUtil import TelegramUtil
from core_loop import main_loop

# Modify argument_parser.py to read new arguments
from argument_parser import parse_args
import on_call


if __name__ == "__main__":
    print("Initializing the pybliotecario")
    teleAPI = TelegramUtil()

    args = parse_args()

    if args.daemon:
        print("Activating main loop")
        while True:
            main_loop(teleAPI)
    else:
        on_call.run_command(args)
