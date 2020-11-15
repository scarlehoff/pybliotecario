"""
    Wrapper for argument parser and initialization
"""
import os
import glob
import importlib
import configparser
from argparse import ArgumentParser, Action

CONFIG_FILE = "pybliotecario.ini"


def write_config(config_dict, config_file, config_exists=False):
    """
    Receives a dictionary of dictionaries and makes it into a
    ConfigParser
    """
    config = configparser.ConfigParser()
    if config_exists:
        config.read(config_file)
    for key, item in config_dict.items():
        config[key] = item
    with open(config_file, "w") as f:
        config.write(f)


def check_attr(attr):
    """
    Checks whether the attr is a class and whether
    it does inherit from Component and whether
    """
    from pybliotecario.components.component_core import Component

    if not isinstance(attr, type):
        return False
    if attr == Component:
        return False
    if issubclass(attr, Component):
        # Is there a more elegant way of knowing whether a method is overriden?
        return not Component.configure_me.__code__ == attr.configure_me.__code__
    return False


def config_module(module):
    """
    Calls the .configure_me method of all modules which
    inherit from component_core.Component
    """
    actor_list = []
    for name in dir(module):
        name_py = getattr(module, name)
        if check_attr(name_py):
            actor_list.append(name_py)
    dict_list = []
    for Actor in actor_list:
        name = Actor.whoamI()
        yn = input("Do you want to configure {0} now? [yn] ".format(name))
        if not yn.lower().startswith(("y", "s")):
            continue
        result = Actor.configure_me()
        if result:
            dict_list.append(result)
    return dict_list


def configure_telegram(main_folder):
    """ Configure Telegram """
    # Initialize the bot in telegram
    print(
        """Welcome to The Wizard!
The first thing you will need is an authorization token from the botfather.
If you don't know how to get one, read here: https://core.telegram.org/bots#6-botfather"""
    )
    token = input("Authorization token: ")
    print("Thanks, let's test this out. Say something to your bot")
    from pybliotecario.backend import TelegramUtil

    teleAPI = TelegramUtil(token, timeout=20)
    while True:
        all_updates = teleAPI.get_updates(not_empty=True)
        from pybliotecario.backend.telegram_util import TelegramMessage

        update = Message(all_updates[0])
        print("Message received: {0}".format(update.text))
        yn = input("Was this your msg? [y/n] ")
        if yn.lower() in ("y", "s"):
            chat_id = update.chat_id
            print("Your chat id is: {0} and your username is: {1}".format(chat_id, update.username))
            break
        print("Try again")
    # Fill the DEFAULT options
    config_dict = {"DEFAULT": {"TOKEN": token, "chat_id": chat_id, "main_folder": main_folder}}
    return config_dict


def configure_all():
    """Import everything inside the components folder that
    inherint from Component and run config_module
    on it"""
    config_dict = {}
    # Import everything that inherits from Component
    import pybliotecario.components as components

    folder_components = os.path.dirname(components.__file__)
    module_components = components.__name__
    modules = glob.glob(folder_components + "/*.py")
    for module_file in modules:
        module_name = "{0}.{1}".format(module_components, os.path.basename(module_file))
        module_clean = module_name.replace(".py", "")
        module = importlib.import_module(module_clean)
        dict_list = config_module(module)
        for dictionary in dict_list:
            for key, item in dictionary.items():
                config_dict[key] = item
    return config_dict


class InitAction(Action):
    """
    This class performs the initialization.

    Everything is only imported exactly where it is needed because that way
    also serves a a sort of documentation? I think. It looks instructive...
    """

    def __init__(self, nargs=0, **kwargs):
        super().__init__(nargs=nargs, **kwargs)

    def __call__(self, parser, *args, **kwargs):
        """
        Configures the pybliotecario by first
        configuring Telegram
        and then calling the configure_me method of all components
        """
        config_dict = {}
        # Set up environmental stuff
        home = os.environ["HOME"]
        main_folder = home + "/.pybliotecario/"
        os.makedirs(main_folder, exist_ok=True)
        config_file = home + "/." + CONFIG_FILE
        # Check whether a config file already exists
        config_exists = os.path.isfile(config_file)
        # If it does you might not want to reconfigure Telegram, so let's ask
        initialize = True
        if config_exists:
            print(
                """It seems pybliotecario's Telegram capabilities
have already been configured in this computer"""
            )
            yn = input("Do you want to configure it again? [y/n] ")
            if not yn.lower().startswith(("y", "s")):
                initialize = False
        if initialize:
            config_dict.update(configure_telegram(main_folder))
        print("Let's loop over the pybliotecario modules to configure their options")
        config_dict.update(configure_all())
        # And finally write the config file
        write_config(config_dict, config_file, config_exists=config_exists)
        parser.exit(0)


def parse_args(args):
    """ Wrapper for ArgumentParser """
    parser = ArgumentParser()
    parser.add_argument(
        "--init",
        help="Wizard to configure the pybliotecario for the first time",
        action=InitAction,
    )
    parser.add_argument("--config_file", help="Define a custom configuration file")
    parser.add_argument("--backend", help="Choose backend: telegram (default), facebook", type=str, default="Telegram")

    parser_cmd = parser.add_argument_group("Command line program")
    parser_cmd.add_argument("message", help="Message to send to Telegram", nargs="*")
    parser_cmd.add_argument("-i", "--image", help="Send image to Telegram")
    parser_cmd.add_argument("-f", "--file", help="Send file to Telegram")

    parser_dae = parser.add_argument_group("Pybliotecarion daemon")
    parser_dae.add_argument("-d", "--daemon", help="Activate the librarian", action="store_true")
    parser_dae.add_argument(
        "--debug",
        help="Write everything to terminal instead of writing to log file",
        action="store_true",
    )
    parser_dae.add_argument(
        "--clear_incoming",
        help="Clears incoming messages in case something has gone wrong",
        action="store_true",
    )
    parser_dae.add_argument(
        "--exit_on_msg",
        help="Exit after receiving the first batch of messages",
        action="store_true",
    )

    parser_com = parser.add_argument_group("Pybliotecario's components")
    parser_com.add_argument(
        "--arxiv_new",
        help="Send a msg containing a digest of the new submissions to arxiv",
        action="store_true",
    )
    parser_com.add_argument(
        "--weather",
        help="Sends a msg to telegram with the current weather and a small forecast",
        action="store_true",
    )
    parser_com.add_argument(
        "--check_repository",
        help="Sends a msg to telegram with the incoming information for the given repository",
    )
    parser_com.add_argument(
        "--pid",
        help="Monitor a PID and sends a message when the PID is finished",
        type=int,
        nargs="+",
    )
    parser_com.add_argument(
        "--my_ip",
        help="Send to the default chat the current IP of the computer",
        action="store_true",
    )
    return parser.parse_args(args)
