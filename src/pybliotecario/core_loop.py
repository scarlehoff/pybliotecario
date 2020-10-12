from datetime import datetime
import os
import pybliotecario.on_cmd_message as on_cmd_message
import logging

logger = logging.getLogger(__name__)

# After which number of continuous exceptions do we actually fail
_FAILTHRESHOLD = 20


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
                on_cmd_message.act_on_telegram_command(tele_api, message, config)
            elif message.is_file:
                # If the message is a file, save the file and we are done
                file_name = message.text.replace(" ", "")
                file_path = "{0}/{1}".format(monthly_folder(main_folder), file_name)
                result = tele_api.download_file(message.file_id, file_path)
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
            except_counter = 0
        except Exception as e:
            logger.error(f"This message produced an exception: {e}")
            if clear and except_counter < _FAILTHRESHOLD:
                except_counter += 1
                # Ignore exceptions until we reach the threshold
                logger.info(message)
                logger.info("Going for the next message")
            else:
                raise e

    tele_api.act_on_updates(act_on_message, not_empty=True)
