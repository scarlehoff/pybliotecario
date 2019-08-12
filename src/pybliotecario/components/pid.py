"""
    This module contains utilities for interacting with processes of the computer
    in which the bot runs.
    It allows for things like killing a process from Telegram or querying for
    an active process
"""

import psutil
from pybliotecario.components.component_core import Component

import logging

log = logging.getLogger(__name__)


def get_process(pid):
    """ Returns a process object for the given PID """
    exists = psutil.pid_exists(pid)
    proc = None
    if exists:
        try:
            proc = psutil.Process(pid=pid)
        except psutil.NoSuchProcess:
            pass

    if proc is None:
        log.info("WARNING: Process {0} was not found".format(pid))

    return proc


def wait_for_it_until_finished(pids):
    """ Receives a list of PIDs and wait for them """
    processes = [get_process(i) for i in pids]
    psutil.wait_procs(processes)


def is_it_alive(data):
    """ Given a pid or a string, check whether
    there is any matching process alive """
    alive = False
    matches = []
    if data.isdigit():
        alive = psutil.pid_exists(int(data))
    else:
        all_active_processes = psutil.process_iter()
        for proc in all_active_processes:
            cmdline = proc.cmdline()
            for info in cmdline:
                if data in info:
                    matches.append("PID: {0}, {1}".format(proc.pid, " ".join(cmdline)))
                    alive = True
    if alive:
        msg = "{0} is alive".format(data)
        if matches:
            msg += "\nI found the following matching processes: \n > {0}".format("\n > ".join(matches))

    else:
        msg = "{0} not found among active processes".format(data)
    return msg


def kill_pid(pid):
    """ Kills the given pid """
    process = get_process(pid)
    if process is not None:
        process.kill()
        return "{0} killed".format(pid)
    else:
        return "No process with pid {0}".format(pid)


class ControllerPID(Component):
    """
    """

    def cmdline_command(self, args):
        """ Waits until the given PID(s) are finished """
        log.info("Waiting for the given PIDs: {0}".format(args.pid))
        wait_for_it_until_finished(args.pid)

    @staticmethod
    def kill(pid):
        """ Kills the received PID """
        return kill_pid(pid)

    @staticmethod
    def alive(pid):
        """ Check whether a PID (or str for searching
        for a PID) is alive """
        return is_it_alive(pid)

    def telegram_message(self, msg):
        if self.check_identity(msg):
            pid_string = msg.text.strip()
            if msg.command == "kill_pid":
                if pid_string.isdigit:
                    return_msg = self.kill(int(pid_string))
                else:
                    return_msg = "{0} is not a PID?".format(pid_string)
            elif msg.command == "is_pid_alive":
                return_msg = self.alive(pid_string)
        else:
            return_msg = "You are not allowed to use this"
        self.send_msg(return_msg)
