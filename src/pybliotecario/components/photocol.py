"""
    Module to save images into an image collection
    with thumbnails and keeping a json as database

    It's a companion to https://github.com/scarlehoff/websito/blob/master/views/foto.pug
"""
from pathlib import Path
from datetime import datetime
import uuid
import json
import logging
from PIL import Image
from pybliotecario.components.component_core import Component

log = logging.getLogger(__name__)
CONFIG = "PHOTOCOL"
ACCEPTED_COMMANDS = ["photocol", "photocol_remove"]


class PhotoCol(Component):
    """
    Save pictures to the photocol folder
    and to the photocol.json database from telegram
    """

    help_text = """ > PhotoCol module
    /photocol comment to add to the picture
    /photocol_remove remove a picture from the db given the unique identifier
    """

    def __init__(self, telegram_object, configuration=None, **kwargs):
        super().__init__(telegram_object, configuration=configuration, **kwargs)
        photocol_config = self.read_config_section(CONFIG)
        self._photofol = Path(photocol_config.get("folder"))
        self._photodb = Path(photocol_config.get("db"))

    def _save_picture(self, file_id):
        """Save the picture to the target folder and creates a thumbnail"""
        unique_name = str(uuid.uuid4())
        file_path = (self._photofol / unique_name).with_suffix(".jpg")
        self.telegram.download_file(file_id, file_path)

        # Create also a thumbnail
        try:
            image = Image.open(file_path)
            aratio = image.width / image.height
            # Keep a resemblance of the original aspect ratio
            size = 240
            thumb_size = (size, int(size/aratio))
            image.thumbnail(thumb_size)
            image.save((self._photofol / "thumbnail" / unique_name).with_suffix(".jpg"))
        except IOError:
            return None

        return file_path

    def _update_db(self, photo_path, comment):
        """Adds a new entry to the json database with the date of (today)
        the path to the picture and a comment
        """
        # Read the previous json if any
        foto_list = []
        if self._photodb.exists():
            foto_list = json.load(self._photodb.open("r", encoding="utf-8"))

        today = datetime.today()
        foto_list.insert(
            0, {"photo": photo_path.name, "date": today.strftime("%d/%m/%Y"), "comment": comment}
        )
        json.dump(foto_list, self._photodb.open("w", encoding="utf-8"), indent=True)

    def _remove_from_db(self, uuid):
        """Remove an entry from the db"""
        test = f"{uuid}.jpg"
        if not self._photodb.exists():
            return self.send_msg("There's no database to remove anything from!")

        foto_list = json.load(self._photodb.open("r", encoding="utf-8"))
        new_json = []
        success = False
        for foto in foto_list:
            if test != foto["photo"]:
                success = True
                new_json.append(foto)

        if success:
            # Create a removed folder to put the picture in
            removed_folder = self._photofol / "removed"
            removed_folder.mkdir(exist_ok = True)

            # Move both picture and thumbnail to removed
            foto_path = self._photofol / test
            foto_thumb = self._photofol / "thumbnail" / test
            foto_path.rename(removed_folder / test)
            foto_thumb.rename(removed_folder / f"{test}-thumb")

            json.dump(new_json, self._photodb.open("w", encoding="utf-8"), indent=True)
            return self.send_msg("Entry removed!")
        else:
            return self.send_msg("That entry was not found in the json db")

    def telegram_message(self, msg):
        if msg.command not in ACCEPTED_COMMANDS:
            return self.send_msg("Command not understood")

        if not self.check_identity(msg):
            self.send_msg("You are not allowed to interact with this command!")
            return

        if msg.command == "photocol_remove":
            return self._remove_from_db(msg.text)

        # Save picture
        photo_path = self._save_picture(msg.file_id)

        if photo_path is None:
            return self.send_msg("There was a problem when creating the thumbnail for this picture")
        # Update json
        self._update_db(photo_path, msg.text)
        self.send_msg("Picture saved")
