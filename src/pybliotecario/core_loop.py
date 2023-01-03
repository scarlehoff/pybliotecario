"""
    This module manages the core loop of the pybliotecario
    when it is called with daemon mode -d
"""
from datetime import datetime
from pathlib import Path
import pybliotecario.on_cmd_message as on_cmd_message
import logging

logger = logging.getLogger(__name__)

# After which number of continuous exceptions do we actually fail
_FAILTHRESHOLD = 20


def _monthly_folder(base_main_folder):
    """Receives a path object with the base main folder
    and returns the monthly folder (also a Path object)"""
    main_folder = base_main_folder / "data"
    ahora = datetime.now()
    y = str(ahora.year)
    m = ahora.strftime("%B")
    folder_name = main_folder / y / m
    folder_name.mkdir(exist_ok=True, parents=True)
    return folder_name


def _write_to_daily_log(main_folder, msg):
    """Write the msg to the daily log"""
    folder = _monthly_folder(main_folder)
    day = datetime.now().day
    file_name = folder / f"{day}.log"
    with file_name.open("a+", encoding="utf-8") as f:
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
    main_folder = Path(config["DEFAULT"]["main_folder"])
    accepted_ids = config.getidlist("DEFAULT", "chat_id")
    main_id = config.getmainid("DEFAULT", "chat_id")
    chivato = config.getboolean("DEFAULT", "chivato", fallback=False)

    except_counter = 0

    # Generate the function to act on Messages
    def act_on_message(message):
        """This function receives a pybliotecario.Message and
        an actor object and calls act_on_telegram_command as required"""
        # Check whether the message should be ignored
        try:  # Wrap everything on a try-except block which will not crash if clear=True
            if message.ignore:
                except_counter = 0
                return
            chat_id = message.chat_id

            # In "chivato" mode, send a message to the main chat_id if sender is not recognized
            if chivato and chat_id not in accepted_ids:
                chivato_msg = f"""El usuario @{message.username} ({chat_id=}) ha enviado el siguiente mensaje:
{message.raw}"""
                tele_api.send_message(chivato_msg, main_id)

            if message.is_command:
                # Call the selected command and act on the message
                on_cmd_message.act_on_telegram_command(tele_api, message, config)
            elif message.is_file:
                # If the message is a file, save the file and we are done
                file_name = message.text.replace(" ", "")
                file_path = _monthly_folder(main_folder) / file_name
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
                _write_to_daily_log(main_folder, message.text)
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
