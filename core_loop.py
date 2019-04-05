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
            "When you're dead I will be still alive"
            ]
    r = randint(0,len(sentences)-1)
    return sentences[r]


def main_loop(teleAPI, clear = False):
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
        try:
            if update.ignore:
                continue
            chatId = update.chatId
            if update.isFile:
                # If the update is a file, save the file and we are done
                file_name = update.text.replace(" ", "")
                file_path = "{0}/{1}".format(monthly_folder(), file_name)
                result = teleAPI.download_file(update.fileId, file_path)
                if result:
                    teleAPI.send_message("¡Archivo recibido y guardado!", chatId)
                    print("File saved to {0}".format(file_path))
                else:
                    teleAPI.send_message("There was some problem with this, sorry", chatId)
                    print("Since there was some problem, let's open a pdb console here and you decide what to do")
                    import pdb
                    pdb.set_trace()
            elif update.is_command:
                # If the update is a command then act on it and don't save the command
                # Generate a response (if any)
                response = on_command.select_command(update.command, update)
                # If the response is a string, just send it as a msg
                if isinstance(response, str):
                    teleAPI.send_message(response, chatId)
                elif isinstance(response, dict):
                    if response['isfile']:
                        filepath = response['filename']
                        teleAPI.send_file(filepath, chatId)
                        if response['delete']:
                            os.remove(filepath)
            else:
                # Otherwise just save the msg to the log and send a funny reply
                write_to_daily_log(update.text)
                random_msg = still_alive()
                teleAPI.send_message(random_msg, chatId)
        except Exception as e:
            # If we are in clear mode, we want to recapture updates to ensure we clear the ones that produce a fail
            # in principle in clear mode we don't care what the fail is about, we just want to clear the failure
            if clear:
                print("\n     > > This update produced an exception: {0}\n\n".format(e))
            else:
                raise e


