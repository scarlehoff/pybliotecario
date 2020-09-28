"""
    Test the system component
"""
import subprocess as sp
from pybliotecario.pybliotecario import main
from pybliotecario.backend import TestUtil
from .conftest import generate_fake_config


def test_uptime(tmp_path, tmpfile):
    """ Checks that the uptime is correct """
    fake_config = generate_fake_config(tmp_path)
    fake_msg = ["/system uptime"]
    test_util = TestUtil(communication_file=tmpfile, fake_msgs=fake_msg)
    args = ["-d", "--exit_on_msg"]
    main(cmdline_arg=args, tele_api=test_util, config=fake_config)
    # Get the uptime from system
    result_cmd = sp.run("uptime", capture_output=True, check=True)
    result = result_cmd.stdout.decode().strip()
    # Get the telegram time
    message = tmpfile.read_text().strip()
    assert result == message
