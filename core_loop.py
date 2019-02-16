from datetime import datetime
import os
from Message import Message
import on_command

def monthly_folder():
    main_folder = "data"
    ahora = datetime.now()
    y = ahora.year
    m = ahora.strftime("%B")
    folder_name = "{0}/{1}/{2}".format(main_folder, y, m)
    if not os.path.isdir(folder_name):
        os.makedirs(folder_name)
    return folder_name

def write_to_daily_log(msg):
    folder = monthly_folder()
    day = datetime.now().day
    file_name = "{0}/{1}.log".format(folder, day)
    with open(file_name, 'a+') as f:
        f.write(msg)
        f.write("\n")

def still_alive():
    from random import randint
    sentences = [
        "Pong",
        "This was a triumph",
        "HUGE SUCCESS",
        "You torn me to pieces",
        "Go ahead and leave me",
        "This cake is great, it's so delicious and moist",
        "Believe me, I am still alive",
        "I'm doing science and I'm still alive",
        "I feel FANTASTIC and I'm still alive",
        "While you're dying I'll be still alive",
        "When you're dead I will be still alive"
    ]
    r = randint(0,len(sentences)-1)
    return sentences[r]


def main_loop(teleAPI):
    """
    This function activates a "listener" and waits for updates from Telegram
    No matter what the update is about, we first store the content and then
    if it is a command, we act on the command
    """
    # Get updates from Telegram
    raw_updates = teleAPI.get_updates(not_empty = True)
    updates = [Message(update) for update in raw_updates]
    # Act on those updates
    for update in updates:
        print(update.json)
        if update.ignore:
            continue
        chatId = update.chatId
        if update.isFile:
            # If the update is a file, save the file and we are done
            file_name = update.text.replace(" ", "")
            file_path = "{0}/{1}".format(monthly_folder(), file_name)
            teleAPI.download_file(update.fileId, file_path)
            teleAPI.send_message("¡Archivo recibido y guardado!", chatId)
        elif update.is_command:
            # If the update is a command then act on it and don't save the command
            # Generate a response (if any)
            response = on_command.select_command(update.command, update)
            # If the response is a string, just send it as a msg
            if isinstance(response, str):
                teleAPI.send_message(response, chatId)
        else:
            # Otherwise just save the msg to the log and send a funny reply
            write_to_daily_log(update.text)
            random_msg = still_alive()
            teleAPI.send_message(random_msg, chatId)


