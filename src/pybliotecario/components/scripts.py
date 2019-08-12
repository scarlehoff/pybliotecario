"""
    Module to run scripts from Telegrma by calling custom commands
    For instant, good_morning will call the command defined in
    /script good_morning will call the command defined in [SCRIPTS] good_morning
"""
import os
import logging
import subprocess as sp
from pybliotecario.components.component_core import Component

log = logging.getLogger(__name__)


class Script(Component):
    section_name = "SCRIPT"

    def __init__(self, telegram_object, **kwargs):
        super().__init__(telegram_object, **kwargs)
        self.blocked = False
        self.scripts = self.read_config_section()
        if not self.scripts:
            self.blocked = True
        default_keys = set(self.configuration["DEFAULT"].keys())
        self.script_names = list(set(self.scripts.keys()) - default_keys)

    def available_commands(self):
        """ Sends a list with the available commands """
        msg_str = "Available commands: " + ", ".join(self.script_names)
        self.send_msg(msg_str)

    @classmethod
    def configure_me(cls):
        print("")
        print(" # Scripts module ")
        print("This is the configuration helper for the scripts module, leave empty to exit")
        dict_out = {cls.section_name: {}}
        while True:
            script_command = input(" Introduce the command name: ")
            sc_cmd = script_command.strip()
            if not sc_cmd:
                break
            script_file = input(" Introduce the path of the command to run with '{0}': ".format(sc_cmd))
            dict_out[cls.section_name][sc_cmd] = script_file
        return dict_out

    def telegram_message(self, msg):
        if not self.check_identity(msg):
            self.blocked = True
            self.send_msg("You are not allowed to run scripts here")
        if self.blocked:
            return
        command_name = msg.text.strip()
        if not msg.has_arguments:
            self.send_msg("Add a command name after /script")
        elif command_name == "list":
            self.available_commands()
        elif command_name not in self.script_names:
            self.send_msg("Command {0} not defined".format(command_name))
            self.available_commands()
        else:
            command_path = self.scripts[command_name]
            log.info("Running: {0}, path: {1}".format(command_name, command_path))
            if os.path.isfile(command_path):
                sp.run([command_path])
                self.send_msg("Command ran")
            else:
                self.send_msg("Script not found")
