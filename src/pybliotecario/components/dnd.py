"""
    Module implementing some functions useful for playing DnD over the internet
"""
import os
import re
import logging
import subprocess as sp
from random import randint
from pybliotecario.components.component_core import Component

log = logging.getLogger(__name__)
# regex to separate +/-
re_pm = re.compile(r"\+|-")
re_mod = re.compile(r"[+-]\d+")

# TODO: write a syntax checker for the diceroll command


def parse_roll(text):
    """
    Gets as input a line of text defining a diceroll command and parses
    it as a list of dice (`dice_list`) a list of signs for each dice (`pm_list`)
    and a list of modifiers (`mod`)
    If the first die has no sign, it adds a '+' sign as default
    """
    # First separate the dice from the modifiers
    modifiers = text.rpartition("d")[-1]
    # Now get all the modifiers (if any)
    nindex = re_pm.search(modifiers)
    if nindex:
        mod = modifiers[nindex.start() :]
        dice = text.partition(mod)[0]
    else:
        mod = ""
        dice = text
    dice_list = re_pm.split(dice)
    pm_list_raw = re_pm.findall(dice)
    if len(pm_list_raw) < len(dice_list):
        pm_list_raw.insert(0, "+")
    # Make the signs into 1 or -1
    pm_list = []
    for i in pm_list_raw:
        if i == "+":
            pm_list.append(1)
        elif i == "-":
            pm_list.append(-1)
    return dice_list, pm_list, mod


def parse_dice(text):
    """Receives a text in the form ndm and returns
    the number of dice and the faces of the die"""
    split_dice = text.split("d")
    n_dice = int(split_dice[0])
    n_face = int(split_dice[-1])
    return n_dice, n_face


def roll_dice(text):
    """
    Receives a string containing any number of dice in rol-like format
    (like 1d20+3d6+4) and returns the number as a result
    """
    # Parse the text command to get the dice and the modifiers
    dice_list, pm_list, mod = parse_roll(text)

    result = []
    for dice, sign in zip(dice_list, pm_list):
        n_dice, n_face = parse_dice(dice)
        for i in range(n_dice):
            result.append(sign * randint(1, n_face))

    # Now sum everything together and add any possible modifiers
    final_result = sum(result)
    final_str = " + ".join(["({0})".format(i) for i in result])

    # Evaluate the modifiers with ast
    if mod.strip():
        modifiers = re_mod.findall(mod)
        for i in modifiers:
            final_result += int(i)
        mod = " ".join(modifiers)
    # And now put all together
    final_str += " {0} = {1}".format(mod, final_result)
    return final_str


class DnD(Component):
    help_text = """ > DnD module
    /r, /roll dice [text]: roll a dice in the format NdM+Mod
    """

    section_name = "DnD"
    default_roll = "1d20"

    def telegram_message(self, msg):
        # Get the text and the username
        text = msg.text.strip()
        username = msg.username.strip()
        # Separate possible extra msgs that go with the text
        split_text = text.split(" ", 1)
        roll_cmd = split_text[0]
        if len(split_text) == 2:
            roll_text = " " + split_text[1]
        else:
            roll_text = ""
        # Compute the result in the form of a string
        roll_result = roll_dice(roll_cmd)
        # Write the answer
        answer = "{0} rolled{1}:\n{2}".format(username, roll_text, roll_result)
        self.send_msg(answer)
