"""
    This module contains a mapping between the command line arguments
    and the components which run them.

    Note that the components are only imported when/if the appropiate command is invoked
    This is a design choice as this way it is not necessary to have all dependencies 
    if you want to run only some submodules of the pybliotecario.

    The most obvious example is running the program just to send msgs and files to Telegram
"""

def run_command(args, teleAPI, config):
    """
    Receives the whole batch of arguments and acts accordingly
    """
    chat_id = config['DEFAULT']['chat_id']
    actors = []

    if args.my_ip:
        from pybliotecario.components.ip_lookup import IpLookup
        actors.append(IpLookup)

    if args.pid:
        """ Wait until the given pid finish, then do whatever else you have been told to do """
        from pybliotecario.components.pid import ControllerPID
        actors.append(ControllerPID)

    if args.weather:
        from pybliotecario.components.weather import Weather
        actors.append(Weather)

    if args.check_repository:
        from pybliotecario.components.repositories import Repository
        actors.append(Repository)

    if args.arxiv_new:
        from pybliotecario.components.arxiv import Arxiv
        actors.append(Arxiv)

    for Actor in actors:
        actor_instance = Actor(teleAPI, chat_id = chat_id, configuration = config)
        actor_instance.cmdline_command(args)

    # These three are the basic commands:
    # send file, send image, send text
    if args.file:
        teleAPI.send_file(args.file, chat_id)
        print("File sent")

    if args.image:
        teleAPI.send_image(args.image, chat_id)
        print("Image sent")

    if args.message:
        message_text = " ".join(args.message)
        teleAPI.send_message(message_text, chat_id)
        print("Message sent")
