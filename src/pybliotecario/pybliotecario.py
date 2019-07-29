#!/usr/bin/env python3
from pybliotecario.TelegramUtil import TelegramUtil
from pybliotecario.configurationData import TOKEN
from pybliotecario.core_loop import main_loop

# Modify argument_parser.py to read new arguments
from pybliotecario.argument_parser import parse_args
import pybliotecario.on_cmdline as on_cmdline

def main():
    print("Initializing the pybliotecario")
    teleAPI = TelegramUtil(TOKEN)

    args = parse_args()

    if args.daemon:
        print("Activating main loop")
        while True:
            main_loop(teleAPI, clear = args.clear_incoming)
    else:
        on_cmdline.run_command(args)

if __name__ == "__main__":
    main()

