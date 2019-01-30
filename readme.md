# pybliotecario

pybliotecario is a simple Telegram bot written en python.
The goal of the program is to mantain an active connection between the computer in which the pybliotecario runs
and your Telegram account.

The program aims to be 100% extensible, running any kind of action in three different fashions:

- On schedule: keep the bot running in the background so it does a series of actions at given times. For instance, calendar reminders.
- On call: just call the command with the proper arguments. For instance, send a msg to your phone.
- On command: write a command to the bot from telegram, so the bot can act on said command.

Adding new actions to each of the different modes is trivial, there are a small example for each case in the relevant files.

## On schedule:

    In order to add new command to be run on schedule just add them to the list you will find in on_schedule.py.

    Example: a command that says "good morning" every day at 8 am

## On call:

    For this it is necessary to modify the file on_call.py. Note that this file reads the arguments defined in argument_parser.py. If you need (surely yes) new command line arguments, this is where you add them.

    Example: -f test.txt, this will send the file named test.txt to your defined Telegram chat

## On command:

    For this it is necessary to modify the file on_command.py
    Comands enter this file through the select_command function, there you need to write a conditional statement for your command and the command to be run.
    Within this function the "message" object containing all information about the message just received is accesible.

    Example: if you send the command /ip, the bot will respond with the current ip of the machine it is running in.


In order to communicate with telegram you will need to instantiate an object of the TelegramUtil class, with the proper TOKEN. For some specific actions you also need the chat id. You can write a general one in the file configurationData, but it is also possible to use a different one per function. 


## TODO:

- IP lookup
- Connection status
- Send any type of files
- Automatise the generation of chatId (atm it needs to be done manually)
- Rationalise Message class to be more than just an organisation feature
- Change "core" into a processUpdate class
