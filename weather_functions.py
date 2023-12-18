import json
import requests
import urllib
import logging

logger = logging.getLogger("weather-telegram")
logger.setLevel(logging.DEBUG)

TOKEN = "6932704235:AAGY_o3kQWhMRdVyKAF6szK7pgZSYQHEgZQ"
OWM_KEY = "1df4df32ac7a88bcb5103cecf493e268"
URL_OWM = "https://api.openweathermap.org/data/2.5/weather?appid={}&units=metric".format(OWM_KEY)


def make_request(url):
    logger.debug("URL: %s" % url)
    r = requests.get(url)
    resp = json.loads(r.content.decode("utf8"))
    return resp


def get_desc(w):
    return w["weather"][0]["description"]


def get_temp(w):
    return w["main"]["temp"]


def get_city(w):
    return w["name"]


def get_weather(place):
    if isinstance(place, dict):  # coordinates provided
        lat, lon = place["latitude"], place["longitude"]
        url = URL_OWM + "&lat=%f&lon=%f&cnt=1" % (lat, lon)
        logger.info("Requesting weather: " + url)
    else:  # place name provided
        url = URL_OWM + "&q={}".format(place)
        logger.info("Requesting weather: " + url)

    js = make_request(url)

    if "cod" in js and js["cod"] == "404":
        return "Sorry, I couldn't find information for the provided location. Please check your spelling and try again."

    logger.debug(js)
    return u"%s \N{DEGREE SIGN}C, %s in %s" % (get_temp(js), get_desc(js), get_city(js))


def send_message(text, chat_id, interface=None):
    text = text.encode('utf-8', 'strict')
    text = urllib.parse.quote_plus(text)
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?text={text}&chat_id={chat_id}&parse_mode=Markdown"
    if interface:
        url += f"&reply_markup={interface}"
    requests.get(url)
