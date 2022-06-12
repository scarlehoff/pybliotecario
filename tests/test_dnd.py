"""
    Tests for the DnD component
"""

import re
from pybliotecario.pybliotecario import main
from pybliotecario.backend import TestUtil
from pybliotecario.components import dnd
from .conftest import generate_fake_config


def test_parse_roll():
    """ Test that the dice is parsed correctly """

    def check_comb(comb):
        dice, signs, modifiers = dnd.parse_roll(comb)
        total = ""
        for die, sign in zip(dice, signs):
            total += "+" if sign == 1 else "-"
            total += die
        if total[0] == "+":
            total = total[1:]
        assert f"{total}{modifiers}" == comb

    trials = ["1d20", "3d20+5d10-2d13+8"]
    for trial in trials:
        check_comb(trial)


def test_msg_roll(tmpfile):
    """
    Test that the rolled number are in the
    requested range
    """
    fake_msg = ["/r 1d20", "/r 4d20+4", "/r 1d20-1d12+12-1"]
    test_util = TestUtil(communication_file=tmpfile, fake_msgs=fake_msg)
    args = ["-d", "--exit_on_msg"]
    fake_config = generate_fake_config(tmpfile)
    main(cmdline_arg=args, tele_api=test_util, config=fake_config)
    messages = tmpfile.read_text().strip()
    results = re.findall(r"(?<==\s)\d*", messages)
    assert 0 < int(results[0]) < 21
    assert 7 < int(results[1]) < 85
    assert -1 < int(results[2]) < 31
