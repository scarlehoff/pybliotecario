from components import ip_lookup

def select_command(tg_command, message_obj):

    if tg_command == "ip":
        return ip_lookup(message_obj.chatId)
