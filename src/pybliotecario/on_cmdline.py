"""
    This module contains a mapping between the command line arguments
    and the components which run them.

    Note that the components are only imported when/if the appropriate command is invoked
    This is a design choice as this way it is not necessary to have all dependencies
    if you want to run only some submodules of the pybliotecario.

    The most obvious example is running the program just to send msgs and files to Telegram
"""

import logging

log = logging.getLogger(__name__)


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

    actors = []

    if args.my_ip:
        from pybliotecario.components.ip_lookup import IpLookup

        actors.append(IpLookup)

    if args.pid:
        from pybliotecario.components.pid import ControllerPID

        actors.append(ControllerPID)

    if args.weather:
        from pybliotecario.components.weather import Weather

        actors.append(Weather)

    if args.check_repository:
        from pybliotecario.components.repositories import Repository

        actors.append(Repository)

    if args.check_github_issues:
        from pybliotecario.components.github_component import Github

        actors.append(Github)

    if args.arxiv_new:
        from pybliotecario.components.arxiv_mod import Arxiv

        actors.append(Arxiv)

    if args.stock_watcher is not None:
        # stock_watcher could be an empty list!
        from pybliotecario.components.stocks import Stocks

        actors.append(Stocks)

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
