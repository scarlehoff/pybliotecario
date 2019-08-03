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
    if result.defaults():
        return result
    else:
        print("Before using this program you need to run the --init option to configure")

def logger_setup(filename):
    """
    Send all logger output to file
    But make sure that errors and warning also go
    to stdout
    """
    # Set the formatter
    formatter = logging.Formatter('[%(levelname)s] - %(message)s')
    # Default handler
    file_handler = logging.FileHandler(filename, 'a')
    file_handler.setFormatter(formatter)
    log.addHandler(file_handler)
    log.setLevel(logging.INFO)
    # Error handler
    error_handler = logging.StreamHandler(sys.stdout)
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.WARNING)
    log.addHandler(error_handler)

def main():
    """ Driver of the pybliotecario """
    args = parse_args()
    config = read_config(args.config_file)
    defaults = config.defaults()
    main_folder = defaults.get("main_folder")
    if not main_folder:
        print("Warning: there is no 'default:main_folder' option set in {0}, using /tmp/".format(args.config_file))
        main_folder = '/tmp/'
    logger_setup(f'{main_folder}/info.log')

    log.info("Initializing the pybliotecario")
    api_token = defaults.get('token')
    if not api_token:
        log.error("No 'default:token' option set in config file, run --init option")
        sys.exit(-1)

    teleAPI = TelegramUtil(api_token)

    on_cmdline.run_command(args, teleAPI, config)

    if args.daemon:
        log.info("Activating main loop")
        while True:
            main_loop(teleAPI, config=config, clear=args.clear_incoming)


if __name__ == "__main__":
    main()
