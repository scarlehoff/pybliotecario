import components as c
import pdb

def select_command(tg_command, message_obj):

    if tg_command == "ip":
        return c.ip_lookup(message_obj.chatId)
    elif tg_command == "arxiv-query":
        from components import arxiv_functions
        arxiv_id = message_obj.text.strip()
        return arxiv_functions.arxiv_query_info(arxiv_id)
    elif tg_command == "arxiv-get":
        from components import arxiv_functions
        arxiv_id = message_obj.text.strip()
        return {'isfile' : True, 'filename' : arxiv_functions.arxiv_get_pdf(arxiv_id), 'delete' : True}


