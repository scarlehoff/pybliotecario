#!/usr/bin/env python3
"""
    Main script for the pybliotecario program
    for command line invocation
"""
import logging
from pathlib import Path
import sys

# Modify argument_parser.py to read new arguments
from pybliotecario.argument_parser import parse_args
from pybliotecario.backend import FacebookUtil, TelegramUtil, TestUtil
from pybliotecario.core_loop import main_loop
from pybliotecario.customconf import CustomConfigParser, default_config_path
import pybliotecario.on_cmdline as on_cmdline

logger = logging.getLogger()


def read_config(config_file=None):
    """Reads the pybliotecario config file and updates the global configuration
    By default looks always in the default file path (in XDG_CONFIG_HOME) and the current folder
    """
    default_file_path = default_config_path()
    # Checks as well (with lower priority) for ~/.pybliotecario.ini for backwards compatibility
    old_path = Path.home() / ".pybliotecario.ini"
    config_files = [old_path, default_file_path, default_file_path.name]
    if old_path.exists():
        logger.error(
            f"Deprecation notice: ~/.pybliotecario.ini is now deprecated, please move the configuration to {default_file_path}"
        )

    if config_file is not None:
        config_files.append(config_file)
    config = CustomConfigParser()
    config.read(config_files, encoding="UTF-8")
    # Add a custom paster to this config
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
        file_handler = logging.FileHandler(filename, "a", encoding="UTF-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)


def main(cmdline_arg=None, tele_api=None, config=None):
    """Driver of the pybliotecario

    For debugging purposes,
    If the arguments or the backend is inputted to this function
    it will override any command line arguments.

    >>> from pybliotecario.pybliotecario import main
    >>> from pybliotecario.backend import TestUtil
    >>> args = ["This is only a test"]
    >>> tt = TestUtil("/tmp/test.txt")
    >>> main(cmdline_arg=args, tele_api=tt)
    """

    # Parse the input arguments and the configuration file
    if cmdline_arg is None:
        cmdline_arg = sys.argv[1:]
    args = parse_args(cmdline_arg)

    # Parse the configuration file
    if config is None:
        config = read_config(args.config_file)
        defaults = config.defaults()
        main_folder = defaults.get("main_folder")
        if not main_folder:
            logger.warning(
                "No 'default:main_folder' option set in %s, using /tmp/", args.config_file
            )
            main_folder = "/tmp/"
        logger_setup(main_folder + "/info.log", debug=args.debug)

    logger.info("Initializing the pybliotecario")

    # Check the backend the pybliotecario should be using
    if tele_api is None:
        if args.backend.lower() == "telegram":
            api_token = config.defaults().get("token")
            if not api_token:
                logger.error(
                    "No 'default:token' option set in %s, run --init option", args.config_file
                )
                sys.exit(-1)

            tele_api = TelegramUtil(config=config, debug=args.debug)
        elif args.backend.lower() == "test":
            tele_api = TestUtil("/tmp/test_file.txt")
        elif args.backend.lower() == "facebook":
            tele_api = FacebookUtil(config=config, debug=args.debug)
            # Check whether we have chat id
            chat_id = config["FACEBOOK"].get("chat_id")
            if chat_id is not None:
                config.set("DEFAULT", "chat_id", chat_id)

    try:
        on_cmdline.run_command(args, tele_api, config)
    except ModuleNotFoundError as e:
        logger.error("In order to use this option you need to install the module '%s'", e.name)

    if args.daemon:
        logger.info("Activating main loop")
        while True:
            main_loop(tele_api, config=config, clear=args.clear_incoming)
            if args.exit_on_msg:
                break


if __name__ == "__main__":
    main()
