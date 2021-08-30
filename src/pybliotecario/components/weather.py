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


class MyOpenWeather:
    """Wrapper to the pyowm 3 API"""

    def __init__(self, weather_api, **kwargs):
        owm = OWM(weather_api, **kwargs)
        self._owm = owm
        self._mgr = owm.weather_manager()

    def check_current_weather(self, location):
        """Checks the current weather at a specific location"""
        weather = self._mgr.weather_at_place(location).weather

        temp = weather.temperature(unit="celsius")["temp"]
        feels_like = weather.temperature(unit="celsius")["feels_like"]
        stat = weather.detailed_status.lower()
        humid = weather.humidity
        city = location.split(",")[0]

        return f"""Right now we have {stat} in {city}
the current temperature is {temp}°C (humidity={humid}%) and it feels like {feels_like}"""

    def _get_forecast(self, location):
        """Gets the full forecast for a given location"""
        forecast = self._mgr.forecast_at_place(location, "3h")
        return forecast.forecast

    # Telegram-usable wrapper
    def will_it_rain(self, location, hour_range=None):
        """
        Checks the forecast for rain today at the given time range
        """
        if hour_range is None:
            hour_range = (0, 23)
        now = datetime.now()
        min_t = now.replace(hour=int(hour_range[0]))
        max_t = now.replace(hour=int(hour_range[1]))
        forecast = self._get_forecast(location)
        # Loop over the weather we have
        rain_h = []
        rain_p = []
        for weather in forecast:
            if weather.precipitation_probability < 0.4:
                continue
            weather_time = datetime.fromtimestamp(weather.ref_time)
            if weather_time < min_t or weather_time >= max_t:
                continue
            rain_h.append(weather_time.hour)
            rain_p.append(int(weather.precipitation_probability * 100))

        if rain_h:
            rain_str = [f"{i}h ({j}%)" for i, j in zip(rain_h, rain_p)]
            rain_times = ", ".join(rain_str)
            msg = "I find possible rain at the following times: {0} ".format(rain_times)
        else:
            msg = "I can see no rain in my foreseeable future"
        return msg


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
        open_weather = MyOpenWeather(self.api_key)
        # ask whether it will rain in the future
        msg_rain = open_weather.will_it_rain(self.weather_location, self.check_times)
        # ask what is the current weather
        msg_current = open_weather.check_current_weather(self.weather_location)
        # join everything on a nice msg and send
        weather_msg = "{1}\n{0}".format(msg_rain, msg_current)
        self.send_msg(weather_msg)
        log.info("Weather information sent")


if __name__ == "__main__":
    from pybliotecario.pybliotecario import logger_setup
    logger_setup(tempfile.TemporaryFile(), debug=True)
    log.info("Testing weather")
    weather_api = "<weather API>"
    city = "Milano, IT"
    owm = MyOpenWeather(weather_api)
    crw = owm.check_current_weather(city)
    log.info(crw)
    msg = owm.will_it_rain(city)
    log.info(msg)
