from pybliotecario.configurationData import chatId
import urllib.request

def ip_lookup(asker_chatid, force = False):
    if str(asker_chatid) == chatId or force:
        external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
        return external_ip
    else:
        return "You are not allowed to see this"
