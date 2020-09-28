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
import sys
import logging

from pybliotecario.argument_parser import CONFIG_FILE

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

    help_text = None

    def __init__(
        self,
        telegram_object,
        chat_id=None,
        configuration=None,
        interaction_chat=None,
        running_in_loop=False,
    ):
        self.telegram = telegram_object
        self.chat_id = chat_id
        if interaction_chat is None:
            self.interaction_chat = chat_id
        else:
            self.interaction_chat = interaction_chat
        self.configuration = configuration
        self.main_folder = self.configuration["DEFAULT"]["main_folder"]
        self.configurable = False
        self.running_in_loop = running_in_loop

    def update_config(self):
        """ Updates default ($HOME/.CONFIG_FILE) configuration file """
        default_config = "{0}/.{1}".format(os.environ.get("HOME"), CONFIG_FILE)
        new_section = self.configure_me()
        for key, item in new_section.items():
            self.configuration[key] = item
        with open(default_config, "w") as f:
            self.configuration.write(f)

    def read_config_section(self, section=None):
        """
        Checks whether section exists within the configuration file
        returns None if it doesn't

        If the bot is running in daemon/receiving from Telegram mode, can't configure
        """
        if section is None:
            section = self.section_name
        try:
            section_dict = self.configuration[section]
            return section_dict
        except KeyError:
            if self.running_in_loop:
                self.send_msg("Section {0} is not configured and will not work".format(section))
                log.error("Section {0} is not configured, please run --init".format(section))
                return {}
            log.warning("There is no section {0} in configuration file".format(section))
            yesno = input(
                "Do you want to configure? (this will add a new section to $HOME/.{0} [yn] ".format(
                    CONFIG_FILE
                )
            )
            if yesno.lower() in ("y", "s"):
                self.update_config()
                sys.exit(-1)
            else:
                log.error("Exiting with error")
                sys.exit(-1)

    @classmethod
    def whoamI(cls):
        """ Name """
        return cls.__name__

    @classmethod
    def help_msg(cls):
        """ Help msg to send to telegram """
        if cls.help_text:
            return cls.help_text
        else:
            name = cls.whoamI()
            help_str = "Help msg for {0} not implemented".format(name)
            return help_str

    @classmethod
    def configure_me(cls):
        """In first initialization (--init or --config) this method will be called
        if any configuration is needed for the child class, it should be done here"""
        return None

    @staticmethod
    def split_list(comma_separated_str):
        """Receives a string representation of a comma separated list
        and splits it, filters out empty spaces and returns a list"""
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
        """Recevies a `msg` object and then
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
        """Wrapper around API send_msg, if chat_id is not defined
        it will use the chat_id this class was instantiated to"""
        if chat_id is None:
            chat_id = self.interaction_chat
        return self.telegram.send_message(msg, chat_id)

    def send_img(self, imgpath, chat_id=None, delete=False):
        """Wrapper around API send_img, if chat_id is not defined
        will use the chat id this class was instantiated to"""
        if chat_id is None:
            chat_id = self.interaction_chat
        if not os.path.isfile(imgpath):
            self.send_msg("ERROR: failed to send {0}".format(imgpath), chat_id)
        self.telegram.send_image(imgpath, chat_id)
        if delete:
            os.remove(imgpath)

    def send_file(self, filepath, chat_id=None, delete=False):
        """Wrapper around API send_file, if chat_id is not defined
        it will use the chat_id this class was instantiated to.
        It will check for existence of the file and will delete it afterwards if required
        """
        if chat_id is None:
            chat_id = self.interaction_chat
        if not os.path.isfile(filepath):
            self.send_msg("ERROR: failed to send {0}".format(filepath), chat_id)
        self.telegram.send_file(filepath, chat_id)
        if delete:
            os.remove(filepath)
