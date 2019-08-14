"""
    This module contains a mapping between Telegram commands
    (msgs which start with / ) and components which will act on them.

    Note that the components are only imported when/if the appropiate command is invoked
    This is a design choice as this way it is not necessary to have all dependencies
    if you want to run only some submodules of the pybliotecario.
"""

import subprocess as sp
import os
import logging

log = logging.getLogger(__name__)


def act_on_telegram_command(tele_api, message_obj, config):
    """
    Act for a given telegram command
    """
    tg_command = message_obj.command
    chat_id = config["DEFAULT"]["chat_id"]

    if tg_command == "ip":
        from pybliotecario.components.ip_lookup import IpLookup as Actor
    elif tg_command.lower() in ("is_pid_alive", "kill_pid"):
        from pybliotecario.components.pid import ControllerPID as Actor
    elif tg_command in ("arxiv-query", "arxiv", "arxivget", "arxiv-get"):
        from pybliotecario.components.arxiv_mod import Arxiv as Actor
    elif tg_command == "script":
        from pybliotecario.components.scripts import Script as Actor
    elif tg_command in ("r", "roll"):
        from pybliotecario.components.dnd import DnD as Actor
    else:
        log.info("No actor declared for this command: {0}".format(tg_command))
        return None



    actor_instance = Actor(
        tele_api, chat_id=chat_id, configuration=config, interaction_chat=message_obj.chat_id, running_in_loop=True
    )
    return actor_instance.telegram_message(message_obj)
