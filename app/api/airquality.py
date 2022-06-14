import requests
import json

import app.language as language
from app.config_reader import load_config


def get_cities(country):
    file = open('app/api/cities/' + country + ".txt", "r")
    cities = []
    for line in file:
        cities.append(language.text[line[:-1]])
    return cities


def get_response_by_city_name(name):
    config = load_config("config/bot.ini")
    response = requests.get("https://api.waqi.info/feed/" + name + "/?token=" + config.tg_bot.aq_token)
    response = json.loads(response.text)
    if response["status"] == "ok":
        idx = response["data"]["idx"]
        name = response["data"]["city"]["name"]
    else:
        text, aqi = language.aq_aqi_answer(response)
        return False, text, aqi, "NoData", "NoData"
    text, aqi = language.aq_aqi_answer(response)
    return True, text, aqi, idx, name


def get_response_by_location(latitude, longitude):
    config = load_config("config/bot.ini")
    response = requests.get("https://api.waqi.info/feed/geo:" + str(latitude) + ";" + str(longitude) + "/?token=" + config.tg_bot.aq_token)
    response = json.loads(response.text)
    if response["status"] == "ok":
        idx = response["data"]["idx"]
        name = response["data"]["city"]["name"]
    else:
        text, aqi = language.aq_aqi_answer(response)
        return False, text, aqi, "NoData", "NoData"
    text, aqi = language.aq_aqi_answer(response)
    return True, text, aqi, idx, name


def get_response_by_idx(idx):
    config = load_config("config/bot.ini")
    response = requests.get("https://api.waqi.info/feed/@" + str(idx) + "/?token=" + config.tg_bot.aq_token)
    response = json.loads(response.text)
    if response["status"] == "ok":
        return response["data"]["aqi"]
    else:
        return "Error"
