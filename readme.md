[![PyPI version](https://badge.fury.io/py/pybliotecario.svg)](https://badge.fury.io/py/pybliotecario)
![Tests](https://github.com/scarlehoff/pybliotecario/workflows/pytest/badge.svg)

# pybliotecario

pybliotecario is a simple messaging bot written in python.

The goal of the program is to be as extensible as possible, both from the point of view of the possibilities it can offer
(in the form of [components](https://github.com/scarlehoff/pybliotecario/tree/master/src/pybliotecario/components)) and
the backends it can support, which right now includes [Telegram and Facebook](https://github.com/scarlehoff/pybliotecario/tree/master/src/pybliotecario/backend)

With this program one can effortlessly maintain an active connection between the computer in which it runs and your phone!

## Installing the pybliotecario

The pybliotecario program is in [pip](https://pypi.org/project/pybliotecario/)
and the base program can be installed with:

```bash
pip install pybliotecario
```

If you want to install all dependencies for [all components](https://github.com/scarlehoff/pybliotecario/blob/master/pyproject.toml#L30) do

```bash
pip install pybliotecario[full]
```

You can also install it using the development version:

```bash
git clone https://github.com/scarlehoff/pybliotecario.git
cd pybliotecario
python3 -m pip install .
```

A small `systemd_install.sh` script is included in the repository in order to easily daemonize it.

## How to connect the pybliotecario to Telegram
The main backend for the pybliotecario is Telegram, although facebook can also be used (see [here](https://github.com/scarlehoff/pybliotecario/tree/master/src/pybliotecario/backend))
In order to communicate with Telegram is necessary to request an API by talking with Telegram's BotFather bot.
The `--init` option will guide you through the process.

```
pybliotecario --init
```

Remember that if you installed the development version you will need to use instead the name of your computer as executable!

## Configuration of the pybliotecario

All configuration options for the pybliotecario can be found in the `${XDG_CONFIG_HOME}/pybliotecario/pybliotecario.ini` file.
In most systems this resolves to `~/.config/pybliotecario/pybliotecario.ini`.
This file is automatically created (and most of the options filled) by running `--init`
and its syntax follows that of the python default [ConfigParser](https://docs.python.org/3/library/configparser.html).

## Basic usage

Once `--init`` has been run for the first time (and thus the API key is in found in `pybliotecario.ini`)
it is possible to start using the program.
To send a message to your Telegram account run:

```
pybliotecario "Hello world!"
```

Instead, to start receiving messages from your phone you can run with:

```
pybliotecario -d --debug
```

Use the `--debug` flag if you want to see a verbose output of what's happening!


## Extending the pybliotecario 

The program aims to be 100% extensible, running any kind of action in two different modes:

- Command line: just call the command with the proper arguments. For instance, send a msg to your phone.
- Message command: write a command to the bot from telegram, so the bot can act on said command.

Adding new actions to each of the different modes is trivial, there are a small example for each case in the relevant files.

In order to add a new command to the bot you need to modify the file `on_cmdline.py` (for command line arguments) or `on_cmd_message.py` for commands sent from Telegram. 
The easiest course of action is to copy one of the components (in the `components` folder you can see the different modules) and add your own actions.
The simplest of them is probably `components/ip_lookup.py` so have a look at it!



## Message command:

These are command received by the bot in the form `/command Do whatever`. In the file `on_cmd_message.py` just add a new command to the if condition. The command definition will be defined in the variable `tg_command`.

There you can just write the python code to perform the command or add a new component. All the information from the msg the bot just received will be included in the `message_obj` variable. In particular the text will be `message_obj.text`.

Example: if you send the command /ip, the bot will respond with the current ip of the machine it is running in.

### help command

You can ask the pybliotecario at any point to send you a list of the available commands with the msg `/help`:

```
> PID module
    /kill_pid pid: kills a given pid
    /is_pid_alive pid/name_of_program: looks for the given pid or program to check whether it is still alive
 > IP module
    /ip : send the current ip in which the bot is running 
 > Arxiv module
    /arxiv arxiv_id: sends information about the given id
    /arxiv_get arxiv_id: sends the PDF for the given id 
 > Script module
    /script list: list all possible scripts
    /script script_name: execute the given script 
 > DnD module
    /r, /roll dice [text]: roll a dice in the format NdM+Mod
 > Reactions module
    /reaction_save reaction_name: save an image with name reaction_name
    /reaction_list: list all reactions
    /reaction reaction_name: sends the reaction given by reaction_name 
 > Wikipedia module
    /wiki term: search for term in wikipedia, return the summary
    /wiki_full N term: read the full article and return N times the defined summary_size
 > System component
    /system uptime: returns the uptime of the computer in which the bot lives
 > Stocks component
    /stock_price ticker: returns the current price for the given ticker
 > Twitter component:
    /twitter_tl [@user] [N=20]: send the last N tweets from the TL [of user @user]
    /twitter_mentions [N=5]: send the last N mentions
    /twitter_tweet <text>: send a tweet

```


## Command line:

In the file `on_cmdline.py` add a new if condition. You can add your action there as python code. If you want to do something more complicated I suggest you create a new component (pull requests are welcome!)

Note: if you need new command line arguments (you surely do!) don't forget to add them to the end of `argument_parser.py`!

Example: 
```
pybliotecario -i test.jpg
```

this will send the image named `test.img` to your defined Telegram chat

### Available cmd_line options:

- msg: sends msg to Telegram
- -i: sends an image to Telegram (or other backend)
- -f: sends a file to Telegram (or other backend)
- --chat_id: target a specific chat ID (e.g.: `~$ pybliotecario "test" --chat_id 12312` will send the msg "test" to 12312 instead of the`chat_id` defined in the `.ini` file).
- --arxiv_new: sends a msg to Telegram with the latest submissions to arxiv, filtered as you see fit (uses https://github.com/lukasschwab/arxiv.py as API)
- --weather: sends a msg to Telegram with the current weather and some information about the forecast (uses https://github.com/csparpa/pyowm as OpenWeatherMap API, which needs an API key)
- --check_repository: sends a msg to Telegram with the incoming changes to the repository
- --my_ip: send the ip of the bot to the defined telegram user
- --pid: Monitor a process by PID, run all other options after the process has finished.
- --stock_watcher json.file: check information about stocks according to the definitions defined in the component [file](https://github.com/scarlehoff/pybliotecario/blob/master/src/pybliotecario/components/stocks.py)

## Some examples and ideas:
For instance, you can run the pybliotecario every morning at 7:15 a.m. to tell you what are the news in the arxiv today adding a cronjob:

    15 07 * * mon-fri /home/pi/Telegram/pybliotecario/pybliotecario.py --arxiv_new

## Contributing
If you have any new ideas for enhancements or have noticed any bugs, feel free to open an issue or a Pull Request :)
This is a toy-project I am maintaining, but I will do my best to help.
