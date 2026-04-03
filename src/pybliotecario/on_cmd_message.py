"""
This module contains a mapping between Telegram commands
(msgs which start with / ) and components which will act on them.

Note that the components are only imported when/if the appropriate command is invoked
This is a design choice as this way it is not necessary to have all dependencies
if you want to run only some submodules of the pybliotecario.
"""

import logging

from .utils import import_component

log = logging.getLogger(__name__)

EXACT_COMMAND_MAPPING = {
    "ip": ("ip_lookup", "IpLookup"),
    # PID
    "is_pid_alive": ("pid", "ControllerPID"),
    "kill_pid": ("pid", "ControllerPID"),
    # Arxiv
    #     "arxiv_query": ("arxiv_mod", "Arxiv"),
    #     "arxiv": ("arxiv_mod", "Arxiv"),
    #     "arxivget": ("arxiv_mod", "Arxiv"),
    #     "arxiv_get": ("arxiv_mod", "Arxiv"),
    # scripts
    "script": ("scripts", "Script"),
    # dnd
    "r": ("dnd", "DnD"),
    "roll": ("dnd", "DnD"),
    # reactions
    #     "reaction_save": ("reactions", "Reactions"),
    #     "reaction": ("reactions", "Reactions"),
    #     "reaction_list": ("reactions", "Reactions"),
    # system
    "system": ("system", "System"),
    # stocks
    "stock_value": ("stocks", "Stocks"),
}

PREFIX_COMMAND_MAPPING = {
    "wiki": ("wiki", "WikiComponent"),
    "reaction": ("reactions", "Reactions"),
    "arxiv": ("arxiv_mod", "Arxiv"),
}


def send_help(tele_api, chat_id):
    log.info("Sending help msg")
    components = sorted(
        list(set(EXACT_COMMAND_MAPPING.values()).union(set(PREFIX_COMMAND_MAPPING.values())))
    )

    full_help = []
    for module, cls in components:
        try:
            Actor = import_component(module, cls)
            full_help.append(Actor.help_msg())
        except ModuleNotFoundError:
            pass
    tele_api.send_message("\n".join(full_help), chat_id)
    return None


def act_on_telegram_command(tele_api, message_obj, config):
    """
    Act for a given telegram command
    """
    tg_command = message_obj.command.lower()
    chat_id = config["DEFAULT"]["chat_id"]

    try:
        if tg_command in EXACT_COMMAND_MAPPING:
            module_name, class_name = EXACT_COMMAND_MAPPING[tg_command]
        elif any(tg_command.startswith(i) for i in PREFIX_COMMAND_MAPPING):
            for k, (module_name, class_name) in PREFIX_COMMAND_MAPPING.items():
                if tg_command.startswith(k):
                    break
        elif tg_command == "help":
            return send_help(tele_api, chat_id)
        else:
            log.info(f"No actor declared for this command: {tg_command}")
            return None

        Actor = import_component(module_name, class_name)

    except ModuleNotFoundError as e:
        log.error(f"The component {tg_command} raised the following error: {e}")
        return tele_api.send_message(f"Dependencies for {tg_command} are missing", chat_id)

    actor_instance = Actor(
        tele_api,
        chat_id=chat_id,
        configuration=config,
        interaction_chat=message_obj.chat_id,
        running_in_loop=True,
    )
    return actor_instance.telegram_message(message_obj)
