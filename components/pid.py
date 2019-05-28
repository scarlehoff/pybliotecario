import psutil

def wait_for_it_until_finished(pids):
    """ Receives a list of PIDs and wait for them """
    processes = [ psutil.Process(pid = i) for i in pids ]
    psutil.wait_procs(processes)



