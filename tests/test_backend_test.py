"""
    Tests the test backend
"""

from pybliotecario.backend import TestUtil

_FAKEMSGS = ["This is only a test", "Hola, caracola"]


def test_get_updates_fakemsg():
    """Checks that get updates returns messages
    with the input message inside
    """
    test_util = TestUtil(fake_msgs=_FAKEMSGS)
    updates = test_util._get_updates()
    # Check that indeed the update contains only the given message
    assert len(updates) == len(_FAKEMSGS)
    for update, msg in zip(updates, _FAKEMSGS):
        assert update["message"]["text"] == msg


def test_get_updates_tmpfile(tmpfile):
    """Check that if we write updates to the temporary file we get them back"""
    test_util = TestUtil(communication_file=tmpfile)
    tmpfile.write_text("\n".join(_FAKEMSGS))
    updates = test_util._get_updates()
    assert len(updates) == len(_FAKEMSGS)
    for update, msg in zip(updates, _FAKEMSGS):
        assert update["message"]["text"] == msg


def test_act_on_update():
    """ Check that act on update works as expected """
    test_util = TestUtil(fake_msgs=["/test command"])

    # Action function
    def action(msg):
        assert msg.text == "command"
        assert msg.is_command
        assert msg.command == "test"

    test_util.act_on_updates(action)


def test_is_msg_in_file(tmpfile):
    """Check that the utlity to check for a msg in the
    communication file is working"""
    msg = "This is only a test"
    test_util = TestUtil(tmpfile)
    tmpfile.write_text(msg)
    assert test_util.is_msg_in_file(msg)
    assert not test_util.is_msg_in_file("Something different")


def test_send_msg():
    """Checks that upon sending a message it gets returned"""
    test_util = TestUtil()
    msg = "Hola, caracola"
    # test util does not take a chat id for now
    ret = test_util.send_message(msg, None)
    assert ret == msg


def test_send_msg_tmpfile(tmpfile):
    """Checks that upon sending a message it gets written to the
    given file"""
    test_util = TestUtil(tmpfile)
    msg = "Hola, caracola"
    # test util does not take a chat id for now
    test_util.send_message(msg, None)
    assert test_util.is_msg_in_file(msg)
