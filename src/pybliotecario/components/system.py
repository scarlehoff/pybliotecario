"""
    This component contains system-commands to be run
    remotely
"""
import subprocess as sp
from pybliotecario.components.component_core import Component


def run_command(command):
    """Run the given command using subprocess and return the stdout"""
    try:
        result = sp.run(command, capture_output=True, check=True)
        stdout = result.stdout.decode().strip()
    except FileNotFoundError:
        stdout = f"No such command: {command}"
    except sp.CalledProcessError:
        stdout = f"The command {command} failed"
    return stdout


ACCEPTED_COMMANDS = {"uptime": "uptime"}


class System(Component):
    help_text = """ > System component
    /system uptime: returns the uptime of the computer in which the bot lives
    """

    def __init__(self, telegram_object, **kwargs):
        super().__init__(telegram_object, **kwargs)

    def telegram_message(self, msg):
        # Allow only the main user to use system
        if not self.check_identity(msg):
            self.send_msg("You are not allowed to run scripts here")
            return
        command_key = msg.text.strip()
        command_name = ACCEPTED_COMMANDS.get(command_key)
        # Check whether the command is in the accepted_commands dictionary
        if command_name is None:
            self.send_msg(f"Command {command_name} not recognized")
        else:
            self.send_msg(run_command(command_name))
