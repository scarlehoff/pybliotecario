"""
    This module contains a mapping between the command line arguments
    and the components which run them.

    Note that the components are only imported when/if the appropiate command is invoked
    This is a design choice as this way it is not necessary to have all dependencies 
    if you want to run only some submodules of the pybliotecario.

    The most obvious example is running the program just to send msgs and files to Telegram
"""
from pybliotecario.configurationData import chat_id, TOKEN
from pybliotecario.TelegramUtil import TelegramUtil

def run_command(args):
    """
    Receives the whole batch of arguments and acts accordingly
    """

    teleAPI = TelegramUtil(TOKEN)
    actors = []

    if args.my_ip:
        from pybliotecario.components.ip_lookup import IpLookup
        actors.append(IpLookup)

    for Actor in actors:
        actor_instance = Actor(teleAPI, chat_id = chat_id)
        actor_instance.cmdline_command(args)
        

    if args.pid:
        """ Wait until the given pid finish, then do whatever else you have been told to do """
        from pybliotecario.components.pid import wait_for_it_until_finished
        print("Waiting for the given PIDs: {0}".format(args.pid))
        wait_for_it_until_finished(args.pid)

    if args.arxiv_new:
        from pybliotecario.components.arxiv_functions import arxiv_recent_filtered
        from pybliotecario.configurationData import arxiv_filter_dict, arxiv_categories
        msg = arxiv_recent_filtered(arxiv_categories, arxiv_filter_dict)
        teleAPI.send_message(msg, chat_id)
        print("Arxiv information sent")

    if args.weather:
        from pybliotecario.components.weather import will_it_rain, check_current_weather
        from pybliotecario.configurationData import weather_api, weather_location, weather_times
        msg_rain = will_it_rain(weather_location, weather_api, weather_times)
        msg_wthr = check_current_weather(weather_location, weather_api)
        weather_msg = "{1}\n{0}".format(msg_rain, msg_wthr)
        teleAPI.send_message(weather_msg, chat_id)
        print("Weather information sent")

    if args.check_repository:
        from pybliotecario.components import repo_check_incoming
        msg = repo_check_incoming(args.check_repository)
        teleAPI.send_message(msg, chat_id)




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
