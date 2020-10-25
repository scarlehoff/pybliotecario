"""
    Module to run scripts from Telegrma by calling custom commands
    For instant, good_morning will call the command defined in
    /script good_morning will call the command defined in [SCRIPTS] good_morning
"""
import pathlib
import logging
import subprocess as sp
import shlex
from pybliotecario.components.component_core import Component

logger = logging.getLogger(__name__)


def _parse_cmd_args(text, shell=False):
    """Separate script name and its arguments
    If shell == True, then we want to preserve quotations
    """
    split_text = shlex.split(text, posix=not shell)
    script = split_text[0]
    args = split_text[1:]
    return script, args





class Script(Component):
    """
    Run scripts in the remote system using subprocess.run

    This is a security-critical feature of the pybliotecario so you should
    be very careful on how you use it. By default only the `chat_id` accepted
    chat is able to run scripts in order to avoid any person to run scripts in your server.

    In order to add scripts that you want to run to the pybliotecario you have
    to add a [SCRIPT] section to the config file (by default pybliotecario.ini)
    with
        script_alias=/path/to/the/script
    then you can call the script from your telegram by calling:
        /script script_alias <any possible arguments>

    Two security (or insecurity rather) features are included in this component:
        - shell
        - everyone
    These are two options that can be added to the [SCRIPT] section of the config file
    and are off by default:
        - shell: with shell=True, the scripts are called through a system shell
        this is sometimes useful (if you want access to any shell-feature) but it could
        potentially allow any attackers to run _any_ commands in your server.
        On the other hand it also allows _you_ to run any commands.
        - everyone: with everyone=True, the `chat_id` is not checked

    In order to avoid potentially destructive behaviour shell and everyone can not be set
    simultaneously. If you want to do so you will have to change the code manually.
    """

    section_name = "SCRIPT"
    help_text = """ > Script module
    /script list: list all possible scripts
    /script script_name: execute the given script """

    def __init__(self, telegram_object, **kwargs):
        super().__init__(telegram_object, **kwargs)
        self.blocked = False
        script_section = self.read_config_section()
        self.scripts = dict(script_section)

        if not self.scripts:
            self.blocked = True
            return

        # Read the config section for the given keys
        # and if they do exist, remove them from self.scripts
        # I know it is confusing but the previous version was apparently python >3.7 only :(
        self._run_in_shell = self._bool_and_pop(script_section, "shell")
        self._allow_everyone = self._bool_and_pop(script_section, "everyone")

        if self._allow_everyone and self._run_in_shell:
            # Comment this for potentially destructive behaviour
            logger.error("The options `everyone` and `shell` can not be used at the same time!")
            self.send_msg("The script module is blocked due to the use of everyone and shell")
            self.blocked = True

        default_keys = set(self.configuration["DEFAULT"].keys())
        self.script_names = list(set(self.scripts.keys()) - default_keys)

    def _bool_and_pop(self, section, key):
        """Check whether a key exists, read it as a boolean
        and pop-it-out"""
        if key in section:
            try:
                val = section.getboolean(key)
                self.scripts.pop(key)
            except ValueError:
                val = self.scripts.pop(key)
                logger.warning("%s option %s in config file not understood, set to False", key, val)
                val = False
        else:
            val = False
        return val

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
            script_file = input(
                " Introduce the path of the command to run with '{0}': ".format(sc_cmd)
            )
            dict_out[cls.section_name][sc_cmd] = script_file
        return dict_out

    def telegram_message(self, msg):
        if not self.check_identity(msg) and not self._allow_everyone:
            self.blocked = True
            self.send_msg("You are not allowed to run scripts here")
        if self.blocked:
            return

        if not msg.has_arguments:
            self.send_msg("Add a command name after /script")
            return

        script_name, script_args = _parse_cmd_args(msg.text.strip(), self._run_in_shell)
        if script_name == "list":
            self.available_commands()
        elif script_name not in self.script_names:
            self.send_msg("Command {0} not defined".format(script_name))
            self.available_commands()
        else:
            command_path = pathlib.Path(self.scripts[script_name])
            logger.info("Running %s, path: %s", script_name, command_path)
            if script_args:
                logger.info("With args: %s", script_args)
            if command_path.is_file():
                try:
                    if self._run_in_shell:
                        full_cmd = f"{command_path} {' '.join(script_args)}"
                        sp.run(full_cmd, shell=True, check=True, cwd=command_path.parent)
                    else:
                        cmd_list = [f"./{command_path.name}"] + script_args
                        sp.run(cmd_list, check=True, cwd=command_path.parent)
                    self.send_msg(f"Command ran")
                except sp.CalledProcessError:
                    self.send_msg("Command ran but failed")
            else:
                self.send_msg("Script not found")
