"""
    All different components must inherit from the Component class

    If the component `configurable` flag is set to True,
    the installer will call the `configure_me` method of the class.

    Once a command has been registered to a component it will call the
    `telegram_command_parser` or the `cmdline_command_parser`.

    In the simplest scenario (the one considered by this example class)
    the class Component will just pass the text of the msg (or the command)
    to the `act_on_command` or `act_on_message` methods.
"""

class Component:
    """
    This is the base class from which all components should inherit

    Instantiate the class requires a messeger object able to talk with the telegram API
    optionally it can receive a configuration object and a chat_id object.
    In general chat_id will be contained already in the configuration
    however we want to be able to comunicate with chats not included in the comunication,
    that's why it is left as a separate option
    """
    def __init__(self, telegram_object, chat_id = None, configuration = None):
        self.telegram = telegram_object
        self.chat_id = chat_id
        self.configuration = configuration
        self.configurable = False

    def configure_me(self):
        pass

    def check_identity(self, msg):
        """ Checks that the user asking is the correct one """
        if int(self.chat_id) == int(msg.chat_id):
            return True
        else:
            return False

    def telegram_message(self, msg):
        """ Recevies a `msg` object and then
        decides what to do with it.
        The `msg` object includes the Telegram command"""
        self.act_on_message(msg.text.strip())

    def cmdline_command(self, args):
        """
        Receives the full set of arguments (including, of course,
        the one which invoked the class) in case synergies with
        other command line arguments are needed.
        In the most general case, of course, this will just be ignored
        """
        self.act_on_command()

    def act_on_message(self, content = None):
        """ Acts on a received msg """
        self.telegram.send_message("Msg received", self.chat_id)

    def act_on_command(self, content = None):
        """ Acts on a received command """
        self.telegram.send_message("Comand line argument invoked", self.chat_id)

    # Some useful wrappers
    def send_msg(self, *args):
        return self.telegram.send_message(*args)
