import os
import glob
import importlib
import configparser
from argparse import ArgumentParser, Action
from ipdb import set_trace

INITIALIZE = False

def write_config(config_dict, config_file):
    """
        Receives a dictionary of dictionaries and makes it into a
        ConfigParser
    """
    config = configparser.ConfigParser()
    for key, item in config_dict.items():
        config[key] = item
    with open(config_file, 'w') as f:
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
        return True
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
    for actor in actor_list:
        result = actor.configure_me()
        if result:
            dict_list.append(result)
    return dict_list

class InitAction(Action):
    """
        This class performs the initialization.

        Everything is only imported exactly where it is needed because that way
        also serves a a sort of documentation? I think. It looks instructive...
    """
    def __init__(self, nargs=0, **kwargs):
        super().__init__(nargs=nargs, **kwargs)
    def __call__(self, parser, *args, **kwargs):
        # Set up environmental stuff
        home = os.environ['HOME']
        config_folder = home + '/.pybliotecario/'
        config_file = home + '/.pybliotecario.test'
        config_dict = {}
        if INITIALIZE:
            # Initialize the bot in telegram
            print("""Welcome to The Wizard!
    The first thing you will need is an authorization token from the botfather.
    If you don't know how to get one, read here: https://core.telegram.org/bots#6-botfather""")
            token = input("Authorization token: ")
            print("Thanks, let's test this out. Say something to your bot")
            from pybliotecario.TelegramUtil import TelegramUtil
            teleAPI = TelegramUtil(token, timeout = 20)
            while True:
                all_updates = teleAPI.get_updates(not_empty=True)
                from pybliotecario.Message import Message
                update = Message(all_updates[0])
                print("Message received: {0}".format(update.text))
                yn = input("Was this your msg? [y/n] ")
                if yn.lower() in ("y", "s"):
                    chat_id = update.chat_id
                    print("Your chat id is: {0} and your username is: {1}".format(chat_id, update.username))
                    break
                else:
                    print("Try again")
            # Fill the DEFAULT options
            config_dict['DEFAULT'] = {
                'TOKEN' : token,
                'chat_id': chat_id,
                'main_folder' : config_folder,
            }

        # Now initialize all the different options
        print("Next we will run over the different modules of this program to fill some configuration options")
        # Import everything that inherits from Component
        import pybliotecario.components as components
        folder_components = os.path.dirname(components.__file__)
        module_components = components.__name__
        modules = glob.glob(f'{folder_components}/*.py')
        for module_file in modules:
            module_name = "{0}.{1}".format(module_components, os.path.basename(module_file))
            module_clean = module_name.replace(".py","")
            module = importlib.import_module(module_clean)
            dict_list = config_module(module)
            for dictionary in dict_list:
                for key, item in dictionary.items():
                    config_dict[key] = item
        # And finally write the config file
        write_config(config_dict, config_file)
        parser.exit(0)


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("message", help="Message to send to Telegram", nargs="*")
    parser.add_argument("--init", help="Wizard to configure the pybliotecario for the first time", action=InitAction)
    parser.add_argument("--config_file", help="Define a custom configuration file")
    parser.add_argument("-d", "--daemon", help="Activate the librarian", action="store_true")
    parser.add_argument("-i", "--image", help="Send iamge to Telegram")
    parser.add_argument("-f", "--file", help="Send file to Telegram")
    parser.add_argument(
        "--arxiv_new", help="Send a msg containing a digest of the new submissions to arxiv", action="store_true"
    )
    parser.add_argument(
        "--weather", help="Sends a msg to telegram with the current weather and a small forecast", action="store_true"
    )
    parser.add_argument(
        "--check_repository",
        help="Sends a msg to telegram with the incoming information for the given repository (receives the base folder of the repository)",
    )
    parser.add_argument(
        "--clear_incoming", help="Clears incoming messages in case something has gone wrong", action="store_true"
    )
    parser.add_argument("--pid", help="Monitor a PID and sends a message when the PID is finished", type=int, nargs="+")
    parser.add_argument("--my_ip", help="Send to the default chat the current IP of the computer", action="store_true")
    return parser.parse_args()
