# structure  site    https://mastergroosha.github.io/telegram-tutorial-2/fsm/
# structure  github  https://github.com/MasterGroosha/telegram-tutorial-2/tree/master/code/04_fsm


import asyncio
import datetime
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from telegram import ParseMode

from app.config_reader import load_config
from app.handlers import register_handlers
from app.database.database import PostgreSQLDataBase
from app.api.airquality import get_response_by_idx
from app.language import text as language
from app.language import aq_aqi_answer_by_number as aqi_text
from app.api.airtemperature import get_response_by_location


# async def main():
#     config = load_config("config/bot.ini")
#     bot = Bot(token=config.tg_bot.token)
#     dp = Dispatcher(bot, storage=MemoryStorage())
#
#     register_handlers(dp)
#
#     await dp.start_polling()


# =================== Notifications
async def at_send_notification(user_id, item, t_bot):
    if item[4]:
        city, response = await get_response_by_location(item[3], item[2], item[5], True)
        await t_bot.send_message(user_id, response, parse_mode=ParseMode.HTML, disable_notification=False)


async def send_notification(user_id, item, db, t_bot):
    if item[6]:
        response = get_response_by_idx(item[0])
        if response >= int(item[4]) + int(item[5]):
            db.aq_update_aqi(user_id, item[2], response)
            text = language['AQ AQI increased'].format(item[3]) + aqi_text(response)
            await t_bot.send_message(user_id, text, parse_mode=ParseMode.HTML, disable_notification=False)
        elif response <= int(item[4]) - int(item[5]):
            db.aq_update_aqi(user_id, item[2], response)
            text = language['AQ AQI decreased'].format(item[3]) + aqi_text(response)
            await t_bot.send_message(user_id, text, parse_mode=ParseMode.HTML, disable_notification=False)



async def check_info(t_bot):
    db = PostgreSQLDataBase()
    temperature_flag = True

    while True:
        await asyncio.sleep(35)
        now = datetime.datetime.now()
        if now.minute == 0:
            users = db.get_all_users()
            if now.hour == 10:
                if temperature_flag:
                    temperature_flag = False
                    for user in range(len(users)):
                        at_locations = db.at_user_have_locations(int(users[user][0]))
                        for item in at_locations:
                            await at_send_notification(int(users[user][0]), item, t_bot)
            else:
                temperature_flag = True

            for user in range(len(users)):
                aq_locations = db.aq_user_have_locations(int(users[user][0]))
                for item in aq_locations:
                    await send_notification(int(users[user][0]), item, db, t_bot)


if __name__ == '__main__':
    config = load_config("config/bot.ini")
    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher(bot, storage=MemoryStorage())

    register_handlers(dp)

    task = asyncio.ensure_future(check_info(bot))
    task
    executor.start_polling(dp, skip_updates=True)
    #asyncio.run(main())
#https://air-bot-vs.herokuapp.com/