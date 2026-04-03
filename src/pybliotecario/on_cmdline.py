"""
This module contains a mapping between the command line arguments
and the components which run them.

Note that the components are only imported when/if the appropriate command is invoked
This is a design choice as this way it is not necessary to have all dependencies
if you want to run only some submodules of the pybliotecario.

The most obvious example is running the program just to send msgs and files to Telegram
"""

import logging
from .utils import import_component

log = logging.getLogger(__name__)

# maps the CLI commands to module->class
# TODO: the class should always be runner or actor or whatever so that only the module is needed
CMDLINE_MAPPING = {
    "my_ip": ("ip_lookup", "IpLookup"),
    "pid": ("pid", "ControllerPID"),
    "weather": ("weather", "Weather"),
    "check_repository": ("repositories", "Repository"),
    "check_github_issues": ("github_component", "Github"),
    "arxiv_new": ("arxiv_mod", "Arxiv"),
    "stock_watcher": ("stocks", "Stocks"),
}


def run_command(args, tele_api, config):
    """
    Receives the whole batch of arguments and acts accordingly
    """
    chat_id = args.chat_id
    if not chat_id.isnumeric():
        # If the id is not numeric maybe is an alias that we have
        try:
            chat_id = config["ALIAS"][chat_id]
        except KeyError:
            chat_id = ""
    # If after everything, chat_id is still empty:
    if not chat_id:
        chat_id = config["DEFAULT"]["chat_id"]

    # Loop over the possible command line arguments
    actors = []
    for arg_name, (module_name, class_name) in CMDLINE_MAPPING.items():
        arg_val = getattr(args, arg_name, None)
        # We first try to import all of them to check for import problems
        if arg_val:
            actors.append(import_component(module_name, class_name, arg_name))

    for Actor in actors:
        actor_instance = Actor(tele_api, chat_id=chat_id, configuration=config)
        actor_instance.cmdline_command(args)

    # These three are the basic commands:
    # send file, send image, send text
    if args.file:
        tele_api.send_file(args.file, chat_id)
        log.info("File sent")

    if args.image:
        tele_api.send_image(args.image, chat_id)
        log.info("Image sent")

    if args.message:
        message_text = " ".join(args.message)
        # Unescape certain characters that we know to be fine
        message_text = message_text.replace("\\n", "\n")
        tele_api.send_message(message_text, chat_id)
        log.info("Message sent")
