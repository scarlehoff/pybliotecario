import components as c
import pdb

def select_command(tg_command, message_obj):

    if tg_command == "ip":
        return c.ip_lookup(message_obj.chatId)
    if tg_command == "arxiv-query":
        arxiv_id = message_obj.text.strip()
        return c.arxiv_query_info(arxiv_id)
