"""
    This module uses the OpenWeather API to provide
    weather information for given location/given times
    using: https://github.com/csparpa/pyowm
"""

from datetime import datetime
from types import MethodType
import logging
from pyowm import OWM
from pybliotecario.components.component_core import Component

log = logging.getLogger(__name__)


def check_current_weather(self, location):
    """ Checks the current weather at a specific location """
    obs = self.weather_at_place(location)
    weather = obs.get_weather()

    temp = weather.get_temperature(unit="celsius")["temp"]
    stat = weather.get_detailed_status()
    city = location.split(",")[0]

    msg = "Right now we have {0} in {2}, the current temperature is {1}°C"
    return msg.format(stat, temp, city)


def get_forecast(self, location):
    """ Gets the full forecast for a given location """
    forecast = self.three_hours_forecast(location)
    return forecast
    # f = fc.get_forecast()


# Telegram-usable wrapper
def will_it_rain(self, location, hours=None):
    """
    Checks the forecast for rain today at the given times
    """
    if hours is None:
        hours = ["10", "17"]
    forecast = self.get_forecast(location)
    rains = []
    for hour in hours:
        if check_for_rain_today_at(forecast, hour):
            rains.append(hour)
    if rains:
        rain_times = ", ".join(rains)
        msg = "I find rain at the following times: {0} ".format(rain_times)
    else:
        msg = "I can see no rain in my foreseeable future"
    return msg


def check_for_rain_today_at(forecast, hour):
    """
    Receives a forecast object
    Returns true if rain is found at the given hour
    """
    now = datetime.now()
    check = now.replace(hour=int(hour))
    if check > now and forecast.will_be_rainy_at(check):
        return True
    else:
        return False


def open_weather_wrapper(api_key, **kwargs):
    """
    Extends OpenWeather main class to have an instance with the API key already defined
    """
    owm = OWM(api_key, **kwargs)
    owm.check_current_weather = MethodType(check_current_weather, owm)
    owm.get_forecast = MethodType(get_forecast, owm)
    owm.will_it_rain = MethodType(will_it_rain, owm)
    return owm


class Weather(Component):
    """
    Checks the weather forecast at a given location
    at some given times as well as the current forecast at the
    given location and reports to Telegram the findings
    """

    def __init__(self, telegram_object, configuration=None, **kwargs):
        super().__init__(telegram_object, configuration=configuration, **kwargs)
        weather_config = self.read_config_section("WEATHER")
        self.api_key = weather_config.get("api")
        self.weather_location = weather_config.get("location")
        times_str = weather_config.get("times")
        self.check_times = self.split_list(times_str)

    @classmethod
    def configure_me(cls):
        print("")
        print(" # WEATHER MODULE # ")
        print("In order to configure the weather module, you need an API token from OpenWeatherMap")
        print("Go here in order to get one: https://openweathermap.org/appid")
        print(
            "Introduce below the API token, leave empty to skip the configuration of the weather module"
        )
        api = input(" > ")
        if api.strip() == "":
            return None
        print("At which times (comma-separated) do you want to check the weather?")
        times = input(" > ")
        print("In which city?")
        location = input(" > ")
        dict_out = {"WEATHER": {"api": api, "location": location, "times": times}}
        return dict_out

    def cmdline_command(self, args):
        # instantiate open wather object
        open_weather = open_weather_wrapper(self.api_key)
        # ask whether it will rain in the future
        msg_rain = open_weather.will_it_rain(self.weather_location, self.check_times)
        # ask what is the current weather
        msg_current = open_weather.check_current_weather(self.weather_location)
        # join everything on a nice msg and send
        weather_msg = "{1}\n{0}".format(msg_rain, msg_current)
        self.send_msg(weather_msg)
        log.info("Weather information sent")


if __name__ == "__main__":
    log.info("Testing weather")
    weather_api = "<weather api>"
    city = "Milano, IT"
    msg = will_it_rain(city, weather_api)
    log.info("Check of the forecast")
    log.info(msg)
    log.info("Check current weather")
    msg = check_current_weather(city, weather_api)
    log.info(msg)
