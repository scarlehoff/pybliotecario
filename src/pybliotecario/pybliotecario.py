#!/usr/bin/env python3
import configparser
import os

from pybliotecario.TelegramUtil import TelegramUtil
from pybliotecario.core_loop import main_loop

# Modify argument_parser.py to read new arguments
from pybliotecario.argument_parser import parse_args
import pybliotecario.on_cmdline as on_cmdline

import logging
log = logging.getLogger()

# Now read the configuration file
CONFIG_FILE = "pybliotecario.ini"


def read_config(config_file=None):
    if config_file is None:
        # Check first in this directory and afterwards in HOME/.pybliotecario.ini
        config_files = [CONFIG_FILE, "{0}/.{1}".format(os.environ.get("HOME"), CONFIG_FILE)]
    else:
        config_files = [config_file]
    for possible_config in config_files:
        if os.path.isfile(possible_config):
            config = configparser.ConfigParser()
            config.read(possible_config)
            return config

def logger_setup(filename):
    filehandler = logging.FileHandler(filename, 'a')
    log.addHandler(filehandler)
    log.setLevel(logging.INFO)


def main():
    """ Driver of the pybliotecario """
    args = parse_args()
    config = read_config(args.config_file)
    main_folder = config["DEFAULT"]["main_folder"]
    logger_setup(f'{main_folder}/info.log')

    log.info("Initializing the pybliotecario")
    teleAPI = TelegramUtil(config["DEFAULT"]["TOKEN"])

    on_cmdline.run_command(args, teleAPI, config)

    if args.daemon:
        log.info("Activating main loop")
        while True:
            main_loop(teleAPI, config=config, clear=args.clear_incoming)


if __name__ == "__main__":
    main()
