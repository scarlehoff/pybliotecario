"""
    This module contains a mapping between Telegram commands
    (msgs which start with / ) and components which will act on them.

    Note that the components are only imported when/if the appropiate command is invoked
    This is a design choice as this way it is not necessary to have all dependencies 
    if you want to run only some submodules of the pybliotecario.
"""

from pybliotecario.configurationData import chat_id
import pybliotecario.components as c
import subprocess as sp
import os
import pdb

def act_on_telegram_command(teleAPI, message_obj):
    """
    Act for a given telegram command
    """
    tg_command = message_obj.command
    if tg_command == "ip":
        from pybliotecario.components.ip_lookup import IpLookup as Actor

    elif tg_command.lower() in ("is_pid_alive", "kill_pid"):
        from pybliotecario.components.pid import ControllerPID as Actor

    elif tg_command in ( "arxiv-query", "arxiv" ):
        from pybliotecario.components import arxiv_functions
        arxiv_id = message_obj.text.strip()
        return arxiv_functions.arxiv_query_info(arxiv_id)
    elif tg_command in ("arxivget", "arxiv-get"):
        from pybliotecario.components import arxiv_functions
        arxiv_id = message_obj.text.strip()
        return {'isfile' : True, 'filename' : arxiv_functions.arxiv_get_pdf(arxiv_id), 'delete' : True}
    elif tg_command.lower() in ("goodmorning", "buenosdias", "buenosdías"):
        morning_file = 'good_morning.sh'
        if os.path.isfile(morning_file):
            cmd = "./{0}".format(morning_file)
            sp.run([cmd])
            return "¡Muy buenos días!"
        else:
            return "File {0} does not exist".format(morning_file)

    try:
        actor_instance = Actor(teleAPI, chat_id = chat_id)
        return actor_instance.telegram_message(message_obj)
    except:
        print("No actor declared for this command: {0}".format(tg_command))
        return None
