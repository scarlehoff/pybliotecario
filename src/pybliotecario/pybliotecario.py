#!/usr/bin/env python3
import configparser
import sys
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
    result = None
    if config_file is None:
        # Check first in this directory and afterwards in HOME/.pybliotecario.ini
        config_files = [CONFIG_FILE, "{0}/.{1}".format(os.environ.get("HOME"), CONFIG_FILE)]
    else:
        config_files = [config_file]
    for possible_config in config_files:
        if os.path.isfile(possible_config):
            config = configparser.ConfigParser()
            config.read(possible_config)
            result = config
            break
    if result and result.defaults():
        return result
    else:
        print("Before using this program you need to run the --init option in order to configure it")
        sys.exit(-1)


def logger_setup(filename, debug = False):
    """
    Send all logger output to file
    But make sure that errors and warning also go
    to stdout
    """
    # Set the formatter
    formatter = logging.Formatter("[%(levelname)s] - %(message)s")
    if debug:
        file_handler = logging.StreamHandler(sys.stdout)
    else:
        # Error handler (not necessary when debug is on):
        error_handler = logging.StreamHandler(sys.stdout)
        error_handler.setFormatter(formatter)
        error_handler.setLevel(logging.WARNING)
        log.addHandler(error_handler)
        # Default handler
        file_handler = logging.FileHandler(filename, "a")
    file_handler.setFormatter(formatter)
    log.addHandler(file_handler)
    log.setLevel(logging.INFO)


def main():
    """ Driver of the pybliotecario """
    args = parse_args()
    config = read_config(args.config_file)
    defaults = config.defaults()
    main_folder = defaults.get("main_folder")
    if not main_folder:
        print("Warning: there is no 'default:main_folder' option set in {0}, using /tmp/".format(args.config_file))
        main_folder = "/tmp/"
    logger_setup(f"{main_folder}/info.log", debug = args.debug)

    log.info("Initializing the pybliotecario")
    api_token = defaults.get("token")
    if not api_token:
        log.error("No 'default:token' option set in config file, run --init option")
        sys.exit(-1)

    tele_api = TelegramUtil(api_token)

    on_cmdline.run_command(args, tele_api, config)

    if args.daemon:
        log.info("Activating main loop")
        while True:
            main_loop(tele_api, config=config, clear=args.clear_incoming)


if __name__ == "__main__":
    main()
