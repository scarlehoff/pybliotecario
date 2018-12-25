from datetime import datetime
import os
from Message import Message

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

def main_loop(teleAPI):
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
            file_name = update.text.replace(" ", "")
            file_path = "{0}/{1}".format(monthly_folder(), file_name)
            teleAPI.download_file(update.fileId, file_path)
            teleAPI.send_message("File recibida!", chatId)
        else:
            write_to_daily_log(update.text)
            teleAPI.send_message("Text recibido", chatId)



