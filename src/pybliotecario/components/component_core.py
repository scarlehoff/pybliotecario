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
    def __init__(self, telegram_object, chat_id, configuration):
        self.telegram = telegram_object
        self.chat_id = chat_id
        self.configuration = configuration
        self.configurable = False

    def configure_me(self):
        pass

    def telegram_message_parser(self, msg):
        """ Recevies a `msg` object and then
        decides what to do with it.
        The `msg` object includes the Telegram command"""
        self.act_on_message(msg.text.strip())

    def cmdline_command_parser(self, command, command_text):
        """ Receives the command which invoked the class
        and the associated text.
        In the simplest case there is only one command, so just
        act on it """
        self.act_on_command(command_text.text_strip())

    def act_on_message(self, msg):
        """ Acts on a received msg """
        self.telegram.send_message("Msg received", self.chat_id)

    def act_on_command(self, command):
        """ Acts on a received command """
        self.telegram.send_message(msg, self.chat_id)
