import pybliotecario.components as c
import subprocess as sp
import os
import pdb

def select_command(tg_command, message_obj):
    """
    Act for a given telegram command
    """
    if tg_command == "ip":
        return c.ip_lookup(message_obj.chatId)
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
    elif tg_command.lower() in ("is_pid_alive"):
        from pybliotecario.components.pid import is_it_alive
        search_string = message_obj.text.strip()
        alive_msg = is_it_alive(search_string)
        return alive_msg
    elif tg_command.lower() in ("kill_pid"):
        from pybliotecario.components.pid import kill_pid
        st = message_obj.text.strip()
        if st.isdigit():
            msg = kill_pid(int(st))
            return msg
        else:
            return "{0} is not a PID?".format(st)

