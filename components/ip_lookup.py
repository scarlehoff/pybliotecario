from configurationData import chatId
import urllib.request

def ip_lookup(asker_chatid):
    if str(asker_chatid) == chatId:
        external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
        return external_ip
    else:
        return "You are not allowed to see this"
