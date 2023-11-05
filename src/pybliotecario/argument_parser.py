"""
    Wrapper for the argument parser and the initialization
"""
from argparse import Action, ArgumentParser, ArgumentTypeError
import configparser
import glob
import importlib
import os
from pathlib import Path

from . import components
from .backend import TelegramUtil
from .backend.telegram_util import TelegramMessage
from .components.component_core import Component
from .customconf import default_config_path, default_data_path


def validpath(value):
    """Check whether the received path is valid"""
    path = Path(value)
    if not path.exists():
        raise ArgumentTypeError(f"The file '{value}' can't be found")
    if path.is_dir():
        raise ArgumentTypeError(f"'{value}' is a directory, only single files can be sent")
    return path


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
        yn = input(f"Do you want to configure {name} now? [yn] ")
        if not yn.lower().startswith(("y", "s")):
            continue
        result = Actor.configure_me()
        if result:
            dict_list.append(result)
    return dict_list


def configure_telegram():
    """Configure pybliotecario to use the Telegram API
    This function walks the user through the process of creating a new bot
    and storing the token and the chat_id of the user in the configuration file
    """
    # Initialize the bot in telegram
    print(
        """Welcome to The Wizard!
The first thing you will need is to create a new bot with the botfather in your telegram client.
Alternatively, you can get use a previously created bot.
Ask the botfather for an authorization token before continuing.
The instructions on how to get the token can be found here: https://core.telegram.org/bots#how-do-i-create-a-bot
"""
    )
    token = input("Authorization token: ")

    # Try to fire up the bot with the given token
    telegram_API = TelegramUtil(token, timeout=20)
    print("Thanks, let's test this out. Say something (anything!) to your bot in telegram")

    for _ in range(20):  # Allow for 20 tries
        all_updates = telegram_API.raw_updates()

        for update in all_updates:
            msg = TelegramMessage(update)
            print(f"Message received: {msg.text}")
            yn = input("Was this your msg? [y/n] ")
            if msg_found := yn.lower().startswith(("y", "s")):
                chat_id = msg.chat_id
                username = msg.username
                print(f"Your chat id is: {chat_id} and your username: {username}")
                break

        if msg_found:
            break

        print("Please, try again")

    else:
        raise ValueError("There was some problem with the configuration of Telegram")

    yn = input(
        "Do you want to enable the 'chivato' mode, so you get a warning if anyone other than you tries to use the bot? [yn] "
    )
    chivato = yn.lower().startswith(("y", "s"))

    # Now prepare the dictionary with the DEFAULT field of the config file
    config_dict = {"DEFAULT": {"TOKEN": token, "chat_id": chat_id, "chivato": chivato}}
    return config_dict


def configure_all():
    """Import everything inside the components folder that
    inherint from Component and run config_module
    on it"""
    config_dict = {}
    missing_dependencies = False

    folder_components = os.path.dirname(components.__file__)
    module_components = components.__name__
    modules = glob.glob(folder_components + "/*.py")
    for module_file in modules:
        module_name = Path(module_file).with_suffix("").name
        try:
            module = importlib.import_module(f"{module_components}.{module_name}")
        except ModuleNotFoundError:
            print(
                f"In order to use the component '{module_name}' it is necessary to install its dependencies"
            )
            missing_dependencies = True
            continue
        dict_list = config_module(module)
        for dictionary in dict_list:
            for key, item in dictionary.items():
                config_dict[key] = item

    if missing_dependencies:
        print(
            """To install missing dependencies for a particular component you can install them explicitly:
    ~$ pip install pybliotecario[component]
or install all dependencies with
    ~$ pip install pybliotecario[full]"""
        )

    return config_dict


class InitAction(Action):
    """
    This class performs the initialization.

    Everything is only imported exactly where it is needed because that way
    also serves as a sort of documentation? I think. It looks instructive...
    """

    def __init__(self, nargs=0, **kwargs):
        super().__init__(nargs=nargs, **kwargs)

    def __call__(self, parser, namespace, *args, **kwargs):
        """
        Configures the pybliotecario by first configuring the Telegram API
        and then calling the ``configure_me`` method of all components
        """
        config_dict = {}

        config_path = default_config_path()
        data_folder = default_data_path()

        if namespace.config_file is not None:
            print(
                f"WARNING! You are setting {namespace.config_file} as the configuration file instead of the default {config_path}"
            )
            yn = input("Are you sure? Do you want to continue [y/n] ")
            if not yn.lower().startswith(("y", "s")):
                print("Don't use --config_file with --init to avoid this!")
                parser.exit(0)
            config_path = namespace.config_file
            data_folder = Path(input(f"Where do you want your data? e.g.: {data_folder}: "))

        print(f"Note: configuration will be written to {config_path}")

        # Make sure the folders exist
        data_folder.mkdir(exist_ok=True, parents=True)
        config_path.parent.mkdir(exist_ok=True, parents=True)

        # Check whether a config file already exists, if it does, ask before doing the Telegram
        initialize = True
        if config_exists := config_path.exists():
            print("It seems pybliotecario has already been initialized in this computer")
            yn = input("Do you want to start the configuration from scratch? [y/n] ")
            initialize = yn.lower().startswith(("y", "s"))

        if initialize:
            config_dict.update(configure_telegram())
            config_dict["DEFAULT"]["main_folder"] = data_folder

        print("Now let's loop over all pybliotecario modules to configure their options")
        config_dict.update(configure_all())
        # And finally write the config file
        write_config(config_dict, config_path, config_exists=config_exists)
        print(f"The configuration of the pybliotecario has been written to: {config_path}")
        parser.exit(0)


def parse_args(args):
    """Wrapper for ArgumentParser"""
    parser = ArgumentParser()
    parser.add_argument(
        "--init", help="Wizard to configure the pybliotecario for the first time", action=InitAction
    )
    parser.add_argument(
        "--config_file",
        help=f"Define a custom configuration file (default: {default_config_path()})",
    )
    parser.add_argument(
        "--backend",
        help="Choose backend: telegram (default), facebook",
        type=str,
        default="Telegram",
    )

    parser_cmd = parser.add_argument_group("Command line program")
    parser_cmd.add_argument("message", help="Message to send to Telegram", nargs="*")
    parser_cmd.add_argument("-i", "--image", help="Send image to Telegram")
    parser_cmd.add_argument("-f", "--file", help="Send file to Telegram", type=validpath)
    parser_cmd.add_argument("--chat_id", help="Chat id to send the message to", default="")

    parser_dae = parser.add_argument_group("Pybliotecario daemon")
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
    parser_com.add_argument("--check_github_issues", help="Get the latest github issues")
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
    parser_com.add_argument(
        "--stock_watcher",
        help="Looks at json file (can be given in config) to watch a number of stocks",
        nargs="*",
    )
    return parser.parse_args(args)
