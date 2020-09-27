"""
    Tests the ip_lookup component
"""

from pybliotecario.pybliotecario import main
from pybliotecario.backend import TestUtil
import socket

def test_cmdline_usage(tmpfile):
    """ Tests that upon --my_ip
    the pybliotecario does sent the ip
    """
    test_util = TestUtil(communication_file=tmpfile)
    args = ["--my_ip"]
    main(cmdline_arg=args, tele_api=test_util)
    # Check whether what we received is a valid IP
    message = tmpfile.read_text().strip()
    socket.inet_aton(message)

def test_msg_usage(tmpfile):
    """ Tests that upon received the message "/ip"
    responds with something that looks like an IP"""
    fake_msg = ["/ip"]
    test_util = TestUtil(communication_file=tmpfile, fake_msgs=fake_msg)
    args = ["-d", "--exit_on_msg"]
    main(cmdline_arg=args, tele_api=test_util)
    # Check whether what we received is a valid IP
    message = tmpfile.read_text().strip()
    # TODO the identity check must be done by the api
#     socket.inet_aton(message)
