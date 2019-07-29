""" Server-helper function to look up the current IP of the program """
from pybliotecario.components.component_core import Component
import urllib.request

def ip_lookup():
    """ Uses ident.me to find out the current ip of the host """
    external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
    return external_ip

class IpLookup(Component):

    def telegram_message(self, msg):
        """ If the chat id asking is the correct one
        sends a msg with the current ip, otherwise fails """
        if self.check_identity(msg):
            send_msg = ip_lookup()
        else:
            send_msg = "You are not allowed to see this"
        self.telegram.send_message(send_msg, msg.chat_id)

    def cmdline_command(self, args):
        """ Sends the current ip to self.chatid """
        # First look for the IP
        my_ip = ip_lookup()
        # Then append it to the text and send it to Telegram
        message_text = " ".join(args.message)
        message = f'{message_text} {my_ip}'
        self.telegram.send_message(message, self.chat_id)
        print(f'IP: {my_ip}')
        # Finally, consume the text
        args.message = None
