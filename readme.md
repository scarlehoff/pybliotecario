# pybliotecario

pybliotecario is a simple Telegram bot written en python.
The goal of the program is to mantain an active connection between the computer in which the pybliotecario runs
and your Telegram account.

The program aims to be 100% extensible, running any kind of action in two different fashions:

- On call: just call the command with the proper arguments. For instance, send a msg to your phone.
- On command: write a command to the bot from telegram, so the bot can act on said command.

Adding new actions to each of the different modes is trivial, there are a small example for each case in the relevant files.

## On call:

For this it is necessary to modify the file on_call.py. Note that this file reads the arguments defined in argument_parser.py. If you need (surely yes) new command line arguments, this is where you add them.

Example: -i test.jpg, this will send the image named test.img to your defined Telegram chat

## On command:

For this it is necessary to modify the file on_command.py
Comands enter this file through the select_command function, there you need to write a conditional statement for your command and the command to be run.
Within this function the "message" object containing all information about the message just received is accesible.

Example: if you send the command /ip, the bot will respond with the current ip of the machine it is running in.


In order to communicate with telegram you will need to instantiate an object of the TelegramUtil class, with the proper TOKEN. For some specific actions you also need the chat id. You can write a general one in the file configurationData, but it is also possible to use a different one per function. 

## Available cmd_line options:
- msg: sends msg to Telegram
- -i: sends a image to Telegram
- -f: sends a file to Telegram
- --arxiv_new: sends a msg to Telegram with the latest submissions to arxiv, filtered as you see fit (uses https://github.com/lukasschwab/arxiv.py as API)

## Available commands
- /ip : tells you the IP where the bot is currently running
- /arxiv-query arxiv_id: returns information on the queried paper
- /arxiv-get arxiv_id: downloads the paper ands sends it to telegram


## TODO:
- Automatise the generation of chatId (atm it needs to be done manually)
