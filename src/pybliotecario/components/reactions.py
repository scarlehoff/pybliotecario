"""
    Module to deal with reaction pics
"""

# TODO:
#   Make sure you don't save img1.png img1.jpg

import glob
import pathlib
import logging
from pybliotecario.components.component_core import Component

log = logging.getLogger(__name__)
REACTIONS = "reactions"


def list_content_folder_as_str(folder):
    """ List the stem of all the files of a folder as a str """
    reaction_wild = f"{folder}/*"
    reaction_content = glob.glob(reaction_wild)
    files_found = [pathlib.Path(i).stem for i in reaction_content]
    files_str = ", ".join(files_found)
    return files_str


def look_for_file(folder, filename):
    """ Receives a `filename` without the extension and looks
    whether it exists in `folder` (with any extension) """
    reaction_wild = f"{folder}/{filename}.*"
    reaction_content = glob.glob(reaction_wild)
    return reaction_content


class Reactions(Component):
    """
        The idea is to upload reactions with:
        /reaction-save blabla (and an image given)
    which will be stored in the folder .pybliotecario/reactions/blabla.png
    and then two options:
        /reaction blabla (which would return the blabla.png image
    and /reaction-list (which would list all files in the reactions folder)
    """

    def __init__(self, telegram_object, configuration=None, **kwargs):
        super().__init__(telegram_object, configuration=configuration, **kwargs)
        self.reaction_folder = f"{self.main_folder}/{REACTIONS}"

    def list_reactions(self):
        """ List the reaction pictures saved in the computer """
        files_str = list_content_folder_as_str(self.reaction_folder)
        out_msg = f"Reaction pics: {files_str}"
        self.send_msg(out_msg)

    def save_reactions(self, msg):
        """ Saves the raction within msg to the reaciton folder """
        file_name = msg.text.replace(" ", "")
        file_path = f"{self.reaction_folder}/{file_name}"
        file_id = msg.fileId
        self.telegram.download_file(file_id, file_path)
        self.send_msg(f"Reaction image {file_name} correctly saved")

    def send_reaction(self, name):
        """ Check whether the file `name` is in the reaction folder and,
        if it is, send it back. it can have any extension! """
        files = look_for_file(self.reaction_folder, name)
        if not files:
            self.send_msg(f"Error: reaction '{name}' not found")
            return
        for reaction in files:
            self.send_img(reaction)

    def telegram_message(self, msg):
        command = msg.command
        if command == "reaction":
            self.send_reaction(msg.text.strip())
        elif command == "reaction_list":
            self.list_reactions()
        elif command == "reaction_save":
            self.save_reactions(msg)
