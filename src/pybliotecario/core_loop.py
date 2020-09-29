from datetime import datetime
import os
from pybliotecario.Message import Message
import pybliotecario.on_cmd_message as on_cmd_message
import logging

logger = logging.getLogger(__name__)

# After which number of continuous exceptions do we actually fail
_FAILTHRESHOLD = 100


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


def main_loop(tele_api, config=None, clear=False):
    """
    This function defines a "listener" which will wait for messages
    in the form of pybliotecario.Message objects and will act on them

    The task of the tele_api is then to call the generated function with an
    instance of the message as the argument.
    This allows the tele_api to do things asynchronously if needed be
    """
    # Check whether we have an accepted user
    if config:
        accepted_user = config["DEFAULT"].get("chat_id")
    else:
        accepted_user = None
    main_folder = config["DEFAULT"]["main_folder"]

    except_counter = 0

    # Generate the function to act on Messages
    def act_on_message(message):
        """This function receives a pybliotecario.Message and
        an actor object and calls act_on_telegram_command as required"""
        # Check whether the message should be ignored
        try:  # Wrap everything on a try-except block wich will not crash if clear=True
            if message.ignore:
                except_counter = 0
                return
            chat_id = message.chat_id
            if message.is_command:
                # Call the selected command and act on the message
                response = on_cmd_message.act_on_telegram_command(tele_api, message, config)
                # If response can be sent to the chat, do so
                # TODO: make this part of a greater BACKEND class
                if isinstance(response, str):
                    tele_api.send_message(response, chat_id)
                elif isinstance(response, dict):
                    if response.get("isfile"):
                        filepath = response.get("filename")
                        tele_api.send_file(filepath, chat_id)
                        if response.get("delete"):
                            os.remove(filepath)
            elif message.isFile:
                # If the message is a file, save the file and we are done
                file_name = message.text.replace(" ", "")
                file_path = "{0}/{1}".format(monthly_folder(main_folder), file_name)
                result = tele_api.download_file(message.fileId, file_path)
                if result:
                    tele_api.send_message("¡Archivo recibido y guardado!", chat_id)
                    logger.info("File saved to %s", file_path)
                else:
                    tele_api.send_message("There was some problem with this, sorry", chat_id)
                    logger.info(message)
                    logger.warning("There was a problem with this update")
            else:
                # Otherwise just save the msg to the log and send a funny reply
                write_to_daily_log(main_folder, message.text)
                random_msg = still_alive()
                tele_api.send_message(random_msg, chat_id)
        except Exception as e:
            logger.error(f"This message produced an exception: {e}")
            if clear and except_counter < _FAILTHRESHOLD:
                # Ignore exceptions until we reach the threshold
                logger.info(message)
                logger.info("Going for the next message")
            else:
                raise e

    tele_api.act_on_updates(act_on_message, not_empty=True)


#
# def main_loop(tele_api, config=None, clear=False):
#     """
#     This function activates a "listener" and waits for updates from Telegram
#     No matter what the update is about, we first store the content and then
#     if it is a command, we act on the command
#     """
#     if config:
#         accepted_user = config["DEFAULT"]["chat_id"]
#     else:
#         accepted_user = None
#     main_folder = config["DEFAULT"]["main_folder"]
#     # Get updates from Telegram
#     raw_updates = tele_api.get_updates(not_empty=True)
#     updates = [Message(update) for update in raw_updates]
#     # Act on those updates
#     for update in updates:
#         logger.info(update.json)
#         try:
#             if update.ignore:
#                 continue
#             chat_id = update.chat_id
#             if update.is_command:
#                 # Calls select command and act on the message
#                 # the function will receive the whole telegram API so it is allowed to send msgs directly
#                 # it can choose to send back a response instead
#                 response = on_cmd_message.act_on_telegram_command(tele_api, update, config)
#                 # if response is text, or file, it will be sent to the chat
#                 if isinstance(response, str):
#                     tele_api.send_message(response, chat_id)
#                 elif isinstance(response, dict):
#                     if response["isfile"]:
#                         filepath = response["filename"]
#                         tele_api.send_file(filepath, chat_id)
#                         if response["delete"]:
#                             os.remove(filepath)
#             elif update.isFile:
#                 # If the update is a file, save the file and we are done
#                 file_name = update.text.replace(" ", "")
#                 file_path = "{0}/{1}".format(monthly_folder(main_folder), file_name)
#                 result = tele_api.download_file(update.fileId, file_path)
#                 if result:
#                     tele_api.send_message("¡Archivo recibido y guardado!", chat_id)
#                     logger.info("File saved to {0}".format(file_path))
#                 else:
#                     tele_api.send_message("There was some problem with this, sorry", chat_id)
#                     logger.info(
#                         "Since there was some problem, let's open a pdb console here and you decide what to do"
#                     )
#
#             else:
#                 # Otherwise just save the msg to the log and send a funny reply
#                 write_to_daily_log(main_folder, update.text)
#                 random_msg = still_alive()
#                 tele_api.send_message(random_msg, chat_id)
#         except Exception as e:
#             # If we are in clear mode, we want to recapture updates to ensure we clear the ones that produce a fail
#             # in principle in clear mode we don't care what the fail is about, we just want to clear the failure
#             if clear:
#                 logger.info("\n     > > This update produced an exception: {0}\n\n".format(e))
#             else:
#                 raise e
