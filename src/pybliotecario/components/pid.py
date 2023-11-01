"""
    This module contains utilities for interacting with processes of the computer
    in which the bot runs.
    It allows for things like killing a process from Telegram or querying for
    an active process
"""

import logging

import psutil

from pybliotecario.components.component_core import Component

logger = logging.getLogger(__name__)


def get_process(pid):
    """Returns a process object for the given PID"""
    exists = psutil.pid_exists(pid)
    proc = None
    if exists:
        try:
            proc = psutil.Process(pid=pid)
        except psutil.NoSuchProcess:
            pass

    if proc is None:
        logger.warning("Process %s was not found", pid)

    return proc


def wait_for_it_until_finished(pids):
    """Receives a list of PIDs and wait for them"""
    processes = []
    for pid in pids:
        proc = get_process(pid)
        if proc is not None:
            processes.append(proc)
    psutil.wait_procs(processes)


def is_it_alive(data):
    """Given a pid or a string, check whether
    there is any matching process alive"""
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
                    command_str = " ".join(cmdline)
                    matches.append(f"PID: {proc.pid}, {command_str}")
                    alive = True
    if alive:
        msg = f"{data} is alive"
        if matches:
            matching_processes = "\n > ".join(matches)
            msg += f"\nI found the following matching processes: \n > {matching_processes}"

    else:
        msg = f"{data} not found among active processes"
    return msg


def kill_pid(pid):
    """Kills the given pid"""
    process = get_process(pid)
    if process is not None:
        process.kill()
        return f"{pid} killed"
    else:
        return f"No process with pid {pid}"


class ControllerPID(Component):
    """Check or kill pids"""

    help_text = """ > PID module
    /kill_pid pid: kills a given pid
    /is_pid_alive pid/name_of_program: looks for the given pid or program to check whether it is still alive"""

    def cmdline_command(self, args):
        """Waits until the given PID(s) are finished"""
        logger.info("Waiting for the given PIDs: %s", args.pid)
        wait_for_it_until_finished(args.pid)

    @staticmethod
    def kill(pid):
        """Kills the received PID"""
        return kill_pid(pid)

    @staticmethod
    def alive(pid):
        """Check whether a PID (or str for searching
        for a PID) is alive"""
        return is_it_alive(pid)

    def telegram_message(self, msg):
        if self.check_identity(msg):
            pid_string = msg.text.strip()
            if msg.command == "kill_pid":
                if pid_string.isdigit():
                    return_msg = self.kill(int(pid_string))
                else:
                    return_msg = f"{pid_string} is not a PID?"
            elif msg.command == "is_pid_alive":
                return_msg = self.alive(pid_string)
            else:
                return_msg = f"Command {msg.command} not understood?"
        else:
            return_msg = "You are not allowed to use this"
        self.send_msg(return_msg)
