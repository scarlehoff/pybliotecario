"""
    Tests the PID module
"""
import time
import subprocess as sp
from multiprocessing.pool import ThreadPool as Pool
from pybliotecario.pybliotecario import main
from pybliotecario.backend import TestUtil
from .conftest import generate_fake_config


def test_cmdline_usage(tmpfile):
    """Tests that upon --pid PID
    the pybliotecario waits until the given PID is finished
    """
    # Send a sleep command to the background
    sleep_cmd = sp.Popen(["sleep", "600s"])
    # Now send a pybliotecario to the background waiting for sleep to finish
    pool = Pool(processes=1)
    test_util = TestUtil(communication_file=tmpfile)
    msg = "Hola, caracola"
    kwargs = {
        "cmdline_arg": [msg, "--pid", str(sleep_cmd.pid), "--debug"],
        "config": generate_fake_config(tmpfile),
        "tele_api": test_util,
    }
    pool.apply_async(main, kwds=kwargs)
    # Check that nothing has yet been written
    if tmpfile.exists():
        assert tmpfile.read_text() == ""
    time.sleep(1)
    # Kill it on its sleep
    sleep_cmd.kill()
    # Wait a few seconds for the dust to settle
    time.sleep(1)
    # Now check that the message has been written
    assert tmpfile.exists()
    assert tmpfile.read_text().strip() == msg


def test_msg_usage_alive(tmpfile):
    """Tests that upon received the message "/is_pid_alive PID"
    responds correctly if it is alive"""
    # Send a sleep command to the background
    sleep_cmd = sp.Popen(["sleep", "600s"])

    fake_msg = [
        f"/is_pid_alive {sleep_cmd.pid}",  # The answer should be yes
        "/is_pid_alive 123456",  # The answer should be no
    ]
    test_util = TestUtil(communication_file=tmpfile, fake_msgs=fake_msg)
    args = ["-d", "--exit_on_msg"]
    fake_config = generate_fake_config(tmpfile)
    main(cmdline_arg=args, tele_api=test_util, config=fake_config)
    # Check whether what we received is a valid IP
    message = tmpfile.read_text().strip().split("\n")
    assert len(message) == 2
    assert "alive" in message[0]
    assert "not found" in message[1]
