import psutil
from pybliotecario.components.component_core import Component


def get_process(pid):
    exists = psutil.pid_exists(pid)
    proc = None
    if exists:
        try:
            proc = psutil.Process(pid=pid)
        except psutil.NoSuchProcess:
            pass

    if proc is None:
        print("WARNING: Process {0} was not found".format(pid))

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
    def cmdline_command(self, args):
        print("Waiting for the given PIDs: {0}".format(args.pid))
        wait_for_it_until_finished(args.pid)

    def telegram_message(self, msg):

        pid_string = msg.text.strip()
        if msg.command == "kill_pid":
            if pid_string.isdigit:
                return_msg = kill_pid(int(pid_string))
            else:
                return_msg = "{0} is not a PID?".format(pid_string)
        elif msg.command == "is_pid_alive":
            return_msg = is_it_alive(pid_string)

        self.send_msg(return_msg, msg.chat_id)
