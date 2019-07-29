#!/usr/bin/env python3
import configparser
import os

from pybliotecario.TelegramUtil import TelegramUtil
from pybliotecario.configurationData import TOKEN
from pybliotecario.core_loop import main_loop

# Modify argument_parser.py to read new arguments
from pybliotecario.argument_parser import parse_args
import pybliotecario.on_cmdline as on_cmdline


# Now read the configuration file
CONFIG_FILE = "pybliotecario.ini"

def read_config(config_file = None):
    if config_file is None:
        # Check first in this directory and afterwards in HOME/.pybliotecario.ini
        config_files = [
                CONFIG_FILE,
                "{0}/.{1}".format(os.environ.get('HOME'), CONFIG_FILE)
                ]
    else:
        config_files = [config_file]
    for possible_config in config_files:
        config = configparser.ConfigParser()
        config.read(possible_config)
        return config

def main():
    """ Driver of the pybliotecario """
    args = parse_args()
    config = read_config(args.config_file)

    print("Initializing the pybliotecario")
    teleAPI = TelegramUtil(config['DEFAULT']['TOKEN'])

    if args.daemon:
        print("Activating main loop")
        while True:
            main_loop(teleAPI, clear = args.clear_incoming)
    else:
        on_cmdline.run_command(args, teleAPI, config)

if __name__ == "__main__":
    main()
