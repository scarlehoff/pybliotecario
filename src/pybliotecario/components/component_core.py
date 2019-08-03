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
import os
import logging
log = logging.getLogger(__name__)


class Component:
    """
    This is the base class from which all components should inherit

    Instantiate the class requires a messeger object able to talk with the telegram API
    optionally it can receive a configuration object and a chat_id object.
    In general chat_id will be contained already in the configuration
    however we want to be able to comunicate with chats not included in the comunication,
    that's why it is left as a separate option
    """

    def __init__(self, telegram_object, chat_id=None, configuration=None):
        self.telegram = telegram_object
        self.chat_id = chat_id
        self.configuration = configuration
        self.configurable = False

    def read_config_section(self, section):
        """
        Checks whether section exists within the configuration file
        returns None if it doesn't
        """
        try:
            section_dict = self.configuration[section]
        except KeyError:
            log.warning(f'There is no section {section} in configuration file')
            yesno = input("Do you want to configure? [yn] ")
            if yesno.lower() in ("y", "s"):
                self.configure_me()
            else:
                log.error("Exiting with error")
                exit(-1)

    @classmethod
    def configure_me():
        """ In first initialization (--init or --config) this method will be called
        if any configuration is needed for the child class, it should be done here """
        return None

    @staticmethod
    def split_list(comma_separated_str):
        """ Receives a string representation of a comma separated list
        and splits it, filters out empty spaces and returns a list """
        list_str = comma_separated_str.strip().split(",")
        filtered_str = filter(lambda x: x, list_str)
        return list(filtered_str)

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

    def act_on_message(self, content=None):
        """ Acts on a received msg """
        self.telegram.send_message("Msg received", self.chat_id)

    def act_on_command(self, content=None):
        """ Acts on a received command """
        self.telegram.send_message("Comand line argument invoked", self.chat_id)

    # Some useful wrappers
    def send_msg(self, msg, chat_id=None):
        """ Wrapper around API send_msg, if chat_id is not defined
        it will use the chat_id this class was instantiated to """
        if chat_id is None:
            chat_id = self.chat_id
        return self.telegram.send_message(msg, chat_id)

    def send_file(self, filepath, chat_id=None, delete=False):
        """ Wrapper around API send_file, if chat_id is not defined
        it will use the chat_id this class was instantiated to.
        It will check for existence of the file and will delete it afterwards if required
        """
        if chat_id is None:
            chat_id = self.chat_id
        if not os.path.isfile(filepath):
            self.send_msg(f"ERROR: failed to send {filepath}", chat_id)
        self.telegram.send_file(filepath, chat_id)
        if delete:
            os.remove(filepath)
