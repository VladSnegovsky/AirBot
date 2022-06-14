import requests
import json

import app.language as language
from app.config_reader import load_config


async def get_response_by_location(latitude, longitude, name, cast):
    config = load_config("config/bot.ini")
    response = requests.get("https://api.openweathermap.org/data/2.5/forecast?lat=" + str(latitude) + "&lon=" + str(
        longitude) + "&units=metric&cnt=24&appid=" + config.tg_bot.at_token)
    response = json.loads(response.text)
    if response["cod"] == "200":
        city = response['city']['name']
        temp_arr = []
        response = response['list']
        for item in response:
            temp_arr.append((str(item['main']['temp']), str(item['dt_txt']), str(item['weather'][0]['main'])))
        return city, await make_answer(city, temp_arr, name, cast)
    else:
        return "Error", language.text['AT There are no information']


async def make_answer(city, temp_arr, name, cast):
    last_date = ""
    if cast:
        answer = language.text['AT Temperature for city'].format(name)
    else:
        answer = language.text['AT Temperature for city'].format(city)

    for item in temp_arr:
        date = item[1][:10]
        time = item[1][11:19]
        if time[0] == '0':
            time = time[1:]
        time = time[:-3]
        #answer = language.text['AT Temperature for time'].format(item[1], item[0], language.text[item[2]])
        if last_date == date:
            answer = answer + "\n  ⏰" + str(time) + " 🌡" + str(item[0].split(".")[0]) + "°C " + language.text[item[2]]
        else:
            answer = answer + "\n\n📅" + str(date)
            answer = answer + "\n  ⏰" + str(time) + " 🌡" + str(item[0].split(".")[0]) + "°C " + language.text[item[2]]
        #answer = answer + language.text['AT Temperature for time'].format(item[1], item[0], language.text[item[2]])
        last_date = date
    return answer
