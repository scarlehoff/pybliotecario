#!/usr/bin/env python3
"""
    Main script for the pybliotecairo program
    for command line invokation
"""
import configparser
import logging
import sys
import os

from pybliotecario.backend import TelegramUtil, TestUtil
from pybliotecario.core_loop import main_loop

# Modify argument_parser.py to read new arguments
from pybliotecario.argument_parser import parse_args, CONFIG_FILE
import pybliotecario.on_cmdline as on_cmdline


logger = logging.getLogger()


def read_config(config_file=None):
    """ Reads the pybliotecario config file and uploads the global configuration """
    config_files = ["{0}/.{1}".format(os.environ.get("HOME"), CONFIG_FILE), CONFIG_FILE]
    if config_file is not None:
        config_files.append(config_file)
    config = configparser.ConfigParser()
    config.read(config_files)
    if config and config.defaults():
        return config
    print("Before using this program you need to run the --init option in order to configure it")
    sys.exit(-1)


def logger_setup(filename, debug=False):
    """
    Send all logger output to file
    But make sure that errors and warning also go
    to stdout
    """
    # Set the formatter
    formatter = logging.Formatter("[%(levelname)s:%(asctime)s] - %(message)s", "%d/%m/%y %H:%M")
    if debug:
        file_handler = logging.StreamHandler(sys.stdout)
    else:
        # Error handler (not necessary when debug is on):
        error_handler = logging.StreamHandler(sys.stdout)
        error_handler.setFormatter(formatter)
        error_handler.setLevel(logging.WARNING)
        logger.addHandler(error_handler)
        # Default handler
        file_handler = logging.FileHandler(filename, "a")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)


def main():
    """ Driver of the pybliotecario """
    # Parse the input arguments and the configuration file
    args = parse_args(sys.argv[1:])
    config = read_config(args.config_file)
    defaults = config.defaults()
    main_folder = defaults.get("main_folder")
    if not main_folder:
        logger.warning("No 'default:main_folder' option set in %s, using /tmp/", args.config_file)
        main_folder = "/tmp/"
    logger_setup(main_folder + "/info.log", debug=args.debug)

    logger.info("Initializing the pybliotecario")
    api_token = defaults.get("token")
    if not api_token:
        logger.error("No 'default:token' option set in %s, run --init option", args.config_file)
        sys.exit(-1)

    # Now check the backend the pybliotecario is working with
    if args.backend.lower() == "telegram":
        tele_api = TelegramUtil(api_token, debug=args.debug)
    elif args.backend.lower() == "test":
        tele_api = TestUtil("/tmp/test_file.txt")

    on_cmdline.run_command(args, tele_api, config)

    if args.daemon:
        logger.info("Activating main loop")
        while True:
            main_loop(tele_api, config=config, clear=args.clear_incoming)


if __name__ == "__main__":
    main()
