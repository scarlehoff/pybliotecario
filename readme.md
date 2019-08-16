[![PyPI version](https://badge.fury.io/py/pybliotecario.svg)](https://badge.fury.io/py/pybliotecario)

# pybliotecario

pybliotecario is a simple Telegram bot written en python.
The goal of the program is to mantain an active connection between the computer in which the pybliotecario runs
and your Telegram account.

# Installing the pybliotecario

The pybliotecario can be installed as other python projects, using pip

`pip install pybliotecario`

o setuptools:

`python3 setup.py install`

When it is installed in this way, the name of the executable will be Hostname (i.e., the name of the computer in which it is running with the first letter capitalized). If you want to use a different name just modify the variable `pybliotecario_name` inside `setup.py`.

In order to link the program with a Telegram bot it is necessary to create a bot talking with Telegram's BotFather. The `--init` option will guide you through the process.

`pybliotecario --init`

A small `systemd_install.sh` script is shipped alongside the github version of the pybliotecario in order to daemonize it easily.

# Configuration of the pybliotecario

All configuration options of the pybliotecario can be found in the file

`$HOME/.pybliotecario.ini`

This file will be automatically created (And most of the options filled) automatically by running `--init`.

# Extending the pybliotecario 

The program aims to be 100% extensible, running any kind of action in two different modes:

- Command line: just call the command with the proper arguments. For instance, send a msg to your phone.
- Message command: write a command to the bot from telegram, so the bot can act on said command.

Adding new actions to each of the different modes is trivial, there are a small example for each case in the relevant files.

In order to add a new command to the bot you need to modify the file `on_cmdline.py` (for command line arguments) or `on_cmd_message.py` for commands sent from Telegram. The easiest course of action is to copy one of the components (in the `components` folder you can see the different modules) and add your own actions. The simplest of them is probably `components/ip_lookup.py` so have a look at it!

## Command line:

In the file `on_cmdline.py` add a new if condition. You can add your action there as python code. If you want to do something more complicated I suggest you create a new component (pull requests are welcome!)

Note: if you need new command line arguments (you surely do!) don't forget to add them to the end of `argument_parser.py`!

Example: -i test.jpg, this will send the image named test.img to your defined Telegram chat

## Message command:

These are command received by the bot in the form `/command Do whatever`. In the file `on_cmd_message.py` just add a new command to the if condition. The command definition will be defined in the variable `tg_command`.

There you can just write the python code to perform the command or add a new component. All the information from the msg the bot just received will be included in the `message_obj` variable. In particular the text will be `message_obj.text`.

Example: if you send the command /ip, the bot will respond with the current ip of the machine it is running in.

## Available cmd_line options:
- msg: sends msg to Telegram
- -i: sends a image to Telegram
- -f: sends a file to Telegram
- --arxiv_new: sends a msg to Telegram with the latest submissions to arxiv, filtered as you see fit (uses https://github.com/lukasschwab/arxiv.py as API)
- --weather: sends a msg to Telegram with the current weather and some information about the forecast (uses https://github.com/csparpa/pyowm as OpenWeatherMap API, which needs an API key)
- --check_repository: sends a msg to Telegram with the incoming changes to the repository
- --my_ip: send the ip of the bot to the defined telegram user
- --pid: Monitor a process by PID, run all other options after the process has finished.

## Available commands
- /ip : tells you the IP where the bot is currently running
- /arxiv-query arxiv_id: returns information on the queried paper
- /arxiv-get arxiv_id: downloads the paper ands sends it to telegram
- /is_pid_alive pid_number/process_name: checks whether a given process is alive 
- /kill_pid: kills the given process in the computer in which the bot is running

## Some examples and ideas:
For instance, you can run the pybliotecario every morning at 7:15 a.m. to tell you what are the news in the arxiv today adding a cronjob:

    15 07 * * mon-fri /home/pi/Telegram/pybliotecario/pybliotecario.py --arxiv_new
