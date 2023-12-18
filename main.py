import json
import time
import logging
import signal
import sys
import requests
from weather_functions import get_weather, send_message

TOKEN = "6932704235:AAGY_o3kQWhMRdVyKAF6szK7pgZSYQHEgZQ"
URL = f"https://api.telegram.org/bot{TOKEN}/"

logger = logging.getLogger("weather-telegram")
logger.setLevel(logging.DEBUG)

chats = {}


def config_logging():
    handler = logging.FileHandler("run.log", mode="w")
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter("[%(levelname)s] - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def sig_handler(signal, frame):
    logger.info("Thank you for using the Genna Weather Bot.......BYE!!!!")
    sys.exit(0)


def handle_updates(updates):
    for update in updates["result"]:
        chat_id = update["message"]["chat"]["id"]
        try:
            text = update["message"]["text"]
        except Exception as e:
            logger.error("No text field in update. Try to get location")
            loc = update["message"]["location"]
            if (chat_id in chats) and (chats[chat_id] == "weatherReq"):
                logger.info("Weather requested for %s in chat id %d" % (str(loc), chat_id))
                send_message(get_weather(loc), chat_id)
                del chats[chat_id]
            continue

        if text == "/weather":
            keyboard = json.dumps(
                {"keyboard": [[{"text": "Share location", "request_location": True}]], "one_time_keyboard": True})
            chats[chat_id] = "weatherReq"
            send_message("Select a city", chat_id, keyboard)
        elif text == "/start":
            send_message("Welcome To GennaWeather!! Please enter the name of a city/country. An incorrect spelling "
                         "will prompt an error message and request to re-enter. Enjoy your time using the app and "
                         "remember, you cant know the weather, unless you're a true genna B)", chat_id)
        elif text.startswith("/"):
            logger.warning("Invalid command %s" % text)
            continue
        else:
            response = get_weather(text)
            send_message(response, chat_id)


def main():
    config_logging()
    signal.signal(signal.SIGINT, sig_handler)

    last_update_id = None
    while True:
        url = f"{URL}getUpdates?timeout=60"
        if last_update_id:
            url += f"&offset={last_update_id}"
        updates = json.loads(requests.get(url).content.decode("utf-8"))

        if len(updates["result"]) > 0:
            last_update_id = max(update["update_id"] for update in updates["result"]) + 1
            handle_updates(updates)
        time.sleep(0.5)


if __name__ == "__main__":
    main()
