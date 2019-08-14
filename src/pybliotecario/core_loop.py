from datetime import datetime
import os
from pybliotecario.Message import Message
import pybliotecario.on_cmd_message as on_cmd_message
import logging

log = logging.getLogger(__name__)


def monthly_folder(base_main_folder):
    main_folder = base_main_folder + "/data"
    ahora = datetime.now()
    y = ahora.year
    m = ahora.strftime("%B")
    folder_name = "{0}/{1}/{2}".format(main_folder, y, m)
    if not os.path.isdir(folder_name):
        os.makedirs(folder_name)
    return folder_name


def write_to_daily_log(main_folder, msg):
    folder = monthly_folder(main_folder)
    day = datetime.now().day
    file_name = "{0}/{1}.log".format(folder, day)
    with open(file_name, "a+") as f:
        f.write(msg)
        f.write("\n")


def still_alive():
    from random import randint

    sentences = [
        "Pong",
        "This was a triumph",
        "HUGE SUCCESS",
        "It's hard to overstate my satisfaction",
        "There's no sense crying over every mistake",
        "You just keep on trying till you run out of cake",
        "I'm being so sincere right now",
        "You tore me to pieces",
        "These points of data make a beautiful line",
        "We're out of beta, we're releasing on time",
        "Think of all the things we learned",
        "Go ahead and leave me",
        "I think I prefer to stay inside",
        "This cake is great, it's so delicious and moist",
        "When I look out there it makes me glad I'm not you",
        "Believe me, I am still alive",
        "I'm doing science and I'm still alive",
        "I feel FANTASTIC and I'm still alive",
        "While you're dying I'll be still alive",
        "When you're dead I will be still alive",
    ]
    r = randint(0, len(sentences) - 1)
    return sentences[r]


def main_loop(teleAPI, config=None, clear=False):
    """
    This function activates a "listener" and waits for updates from Telegram
    No matter what the update is about, we first store the content and then
    if it is a command, we act on the command
    """
    if config:
        accepted_user = config["DEFAULT"]["chat_id"]
    else:
        accepted_user = None
    main_folder = config["DEFAULT"]["main_folder"]
    # Get updates from Telegram
    raw_updates = teleAPI.get_updates(not_empty=True)
    updates = [Message(update) for update in raw_updates]
    # Act on those updates
    for update in updates:
        log.info(update.json)
        try:
            if update.ignore:
                continue
            chat_id = update.chat_id
            if update.isFile:
                # If the update is a file, save the file and we are done
                file_name = update.text.replace(" ", "")
                file_path = "{0}/{1}".format(monthly_folder(), file_name)
                result = teleAPI.download_file(update.fileId, file_path)
                if result:
                    teleAPI.send_message("¡Archivo recibido y guardado!", chat_id)
                    log.info("File saved to {0}".format(file_path))
                else:
                    teleAPI.send_message("There was some problem with this, sorry", chat_id)
                    log.info("Since there was some problem, let's open a pdb console here and you decide what to do")
            elif update.is_command:
                # Calls select command and act on the message
                # the function will receive the whole telegram API so it is allowed to send msgs directly
                # it can choose to send back a response instead
                response = on_cmd_message.act_on_telegram_command(teleAPI, update, config)
                # if response is text, or file, it will be sent to the chat
                if isinstance(response, str):
                    teleAPI.send_message(response, chat_id)
                elif isinstance(response, dict):
                    if response["isfile"]:
                        filepath = response["filename"]
                        teleAPI.send_file(filepath, chat_id)
                        if response["delete"]:
                            os.remove(filepath)
            else:
                # Otherwise just save the msg to the log and send a funny reply
                write_to_daily_log(main_folder, update.text)
                random_msg = still_alive()
                teleAPI.send_message(random_msg, chat_id)
        except Exception as e:
            # If we are in clear mode, we want to recapture updates to ensure we clear the ones that produce a fail
            # in principle in clear mode we don't care what the fail is about, we just want to clear the failure
            if clear:
                log.info("\n     > > This update produced an exception: {0}\n\n".format(e))
            else:
                raise e
