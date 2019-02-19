import pyowm
# https://github.com/csparpa/pyowm

import pdb
from datetime import datetime

def check_current_weather(location, api_key):
    owm = pyowm.OWM(api_key)
    obs = owm.weather_at_place(location)
    w = obs.get_weather()

    temp = w.get_temperature(unit = 'celsius')['temp']
    stat = w.get_detailed_status()
    city = location.split(',')[0]

    msg = "Right now we have {0} in {2}, the current temperature is {1}°C"
    return msg.format(stat, temp, city)

def get_forecast(location, api_key):
    owm = pyowm.OWM(api_key)
    fc = owm.three_hours_forecast(location)
    return fc
    f = fc.get_forecast()

def check_for_rain_today_at(forecast, hour):
    """
    Returns true if rain is found at the given hour
    """
    now = datetime.now()
    check = now.replace(hour = int(hour))
    if check > now and forecast.will_be_rainy_at(check):
        return True
    else:
        return False

# Telegram-usable functions
def will_it_rain(location, api_key, hours = ["10", "17"]):
    """
    Checks the forecast for rain today at the given times
    """
    forecast = get_forecast(location, api_key)
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


if __name__ == "__main__":
    print("Testing weather")
    weather_api = '33f58fa8fd905d895f5f04f8a3c0bdd6'
    city = 'Milano, IT'
    msg = will_it_rain(city, weather_api)
    print("Check of the forecast")
    print(msg)
    print("Check current weather")
    msg = check_current_weather(city, weather_api)
    print(msg)
