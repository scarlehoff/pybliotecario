"""
    This module contains a mapping between Telegram commands
    (msgs which start with / ) and components which will act on them.

    Note that the components are only imported when/if the appropriate command is invoked
    This is a design choice as this way it is not necessary to have all dependencies
    if you want to run only some submodules of the pybliotecario.
"""
import logging
import importlib

log = logging.getLogger(__name__)


def import_component(module, cls):
    module_path = "pybliotecario.components." + module
    module = importlib.import_module(module_path)
    return getattr(module, cls)


def send_help(tele_api, chat_id):
    log.info("Sending help msg")
    components = [
        ("pid", "ControllerPID"),
        ("ip_lookup", "IpLookup"),
        ("arxiv_mod", "Arxiv"),
        ("scripts", "Script"),
        ("dnd", "DnD"),
        ("reactions", "Reactions"),
        ("wiki", "WikiComponent"),
        ("system", "System"),
        ("stocks", "Stocks"),
        ("twitter", "TwitterComponent"),
        ("photocol", "PhotoCol"),
    ]
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
    tg_command = message_obj.command
    chat_id = config["DEFAULT"]["chat_id"]

    try:
        if tg_command == "ip":
            from pybliotecario.components.ip_lookup import IpLookup as Actor
        elif tg_command.lower() in ("is_pid_alive", "kill_pid"):
            from pybliotecario.components.pid import ControllerPID as Actor
        elif tg_command in ("arxiv_query", "arxiv", "arxivget", "arxiv_get"):
            from pybliotecario.components.arxiv_mod import Arxiv as Actor
        elif tg_command == "script":
            from pybliotecario.components.scripts import Script as Actor
        elif tg_command in ("r", "roll"):
            from pybliotecario.components.dnd import DnD as Actor
        elif tg_command in ("reaction_save", "reaction", "reaction_list"):
            from pybliotecario.components.reactions import Reactions as Actor
        elif tg_command[:4] == "wiki":
            from pybliotecario.components.wiki import WikiComponent as Actor
        elif tg_command == "system":
            from pybliotecario.components.system import System as Actor
        elif tg_command == "stock_price":
            from pybliotecario.components.stocks import Stocks as Actor
        elif tg_command.startswith("twitter_"):
            from pybliotecario.components.twitter import TwitterComponent as Actor
        elif tg_command.startswith("photocol"):
            from pybliotecario.components.photocol import PhotoCol as Actor

        elif tg_command == "help":
            return send_help(tele_api, chat_id)
        else:
            log.info("No actor declared for this command: {0}".format(tg_command))
            return None

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
