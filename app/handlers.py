from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text, IDFilter
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from telegram import ParseMode

from app.language import text as language
from app import buttons
from app.database.database import PostgreSQLDataBase
import app.api.airquality as aq
import app.api.airtemperature as at
import app.api.functions as functions

db = PostgreSQLDataBase()


class Menu(StatesGroup):
    instructions = State()
    menu = State()
    at_menu = State()
    aq_menu = State()
    aq_add_location = State()
    aq_select_location_city_by_name = State()
    aq_show_aqi_and_ask = State()
    aq_set_location_name = State()
    aq_set_notifications = State()
    aq_select_location_by_users_location = State()
    aq_select_location_users_location = State()
    aq_my_locations_menu = State()
    aq_user_location_menu = State()
    aq_edit_name = State()
    aq_edit_step = State()

    at_add_location = State()
    at_select_location_by_users_location = State()
    at_show_temp_and_ask = State()
    at_set_location_name = State()
    at_set_notifications = State()
    at_ask_to_change_name = State()
    at_change_location_name = State()
    at_my_locations_menu = State()
    at_user_location_menu = State()
    at_edit_name = State()


async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()

    if not db.user_exists(message.from_user.id):
        db.add_user(message.from_user.id)

    await message.answer(
        language['Instructions'],
        parse_mode=ParseMode.HTML,
        reply_markup=buttons.ok_button()
    )
    await Menu.instructions.set()


async def menu(message: types.Message):
    await message.answer(
        language['Menu'],
        reply_markup=buttons.menu()
    )
    await Menu.menu.set()


async def menu_action(message: types.Message):
    if message.text == language['Air Quality']:
        await message.answer(
            language['AQ Menu'],
            reply_markup=buttons.aq_menu()
        )
        await Menu.aq_menu.set()
    elif message.text == language['Air Temperature']:
        await message.answer(
            language['AT Menu'],
            reply_markup=buttons.at_menu()
        )
        await Menu.at_menu.set()
    elif message.text == language['About This Bot']:
        await message.answer(
            language['help command'],
            parse_mode=ParseMode.HTML
        )


# =========================================== Air Quality
async def aq_menu_action(message: types.Message, state: FSMContext):
    """Функція реагує на натискання кнопок меню Якості Повітря"""
    if message.text == language['Back']:
        await message.answer(
            language['Menu'],
            reply_markup=buttons.menu()
        )
        await Menu.menu.set()
    elif message.text == language['Add Location']:
        await message.answer(
            language['AQ Add Location Menu'],
            reply_markup=buttons.aq_add_location()
        )
        await Menu.aq_add_location.set()
    elif message.text == language['My Locations']:
        locations = db.aq_user_have_locations(message.from_user.id)
        if bool(len(locations)):
            names = functions.aq_get_names_from_locations_list(locations)
            await state.update_data(user_locations=names)
            await message.answer(
                language['AQ Show user locations'],
                reply_markup=buttons.aq_select_city(names)
            )
            await Menu.aq_my_locations_menu.set()
        else:
            await message.answer(
                language['AQ You have no locations']
            )


async def aq_menu_add_location(message: types.Message):
    """Функція реагує на натискання кнопок у меню з вибором способу додавання нової локації"""
    if message.text == language['Select From List']:
        await message.answer(
            language['AQ Select city'],
            reply_markup=buttons.aq_select_city(aq.get_cities('ukraine'))
        )
        await Menu.aq_select_location_city_by_name.set()
    elif message.text == language['Geolocation']:
        await message.answer(
            language['AQ Share your location'],
            reply_markup=buttons.aq_share_location()
        )
        await Menu.aq_select_location_by_users_location.set()
    elif message.text == language['Back']:
        await message.answer(
            language['AQ Menu'],
            reply_markup=buttons.aq_menu()
        )
        await Menu.aq_menu.set()


async def aq_select_location_city_by_name(message: types.Message, state: FSMContext):
    """Функція реагує на натискання кнопок у меню з різними містами"""
    if message.text == language['Back']:
        await message.answer(
            language['AQ Add Location Menu'],
            reply_markup=buttons.aq_add_location()
        )
        await Menu.aq_add_location.set()
    elif message.text in aq.get_cities('ukraine'):  # Якщо користувач натиснув на місто
        success, text, aqi, idx, name = aq.get_response_by_city_name(language[message.text])
        # Отримуємо {результат запиту; текст для відповіді користувачу; стан повітря; id локації; ім'я локації}
        await aq_show_response_in_adding(message, state, success, text, aqi, idx, name)


async def aq_show_aqi_and_ask(message: types.Message, state: FSMContext):
    """Функція реагує на натискання кнопок у меню з запитом на зберігання даної локації"""
    if message.text == language['Yes']:
        user_data = await state.get_data()
        await message.answer(
            language['AQ Enter name for location'].format(user_data['chosen_city']),
            parse_mode=ParseMode.HTML,
            reply_markup=buttons.aq_set_name_for_location()
        )
        await Menu.aq_set_location_name.set()
    elif message.text == language['No']:
        await message.answer(
            language['AQ Menu'],
            reply_markup=buttons.aq_menu()
        )
        await Menu.aq_menu.set()


async def aq_set_location_name(message: types.Message, state: FSMContext):
    """Функція реагує на натискання кнопок та надсилання слів у меню Збереження імені локації"""
    if len(message.text) > 20:  # Довжина не має перевищувати 20 символів
        await message.answer(
            language['AQ Length limit of name'],
        )
    elif db.aq_location_name_exists(message.from_user.id, message.text):
        await message.answer(
            language['AQ Location with such name already exists'],
            reply_markup=types.ReplyKeyboardRemove()
        )
    elif message.text == language['Ok']:  # Реагує на кнопку Ок
        user_data = await state.get_data()
        await message.answer(
            language['AQ Location name will be'].format(user_data['chosen_city']),
            parse_mode=ParseMode.HTML
        )
        await message.answer(
            language['AQ Turn On/Off notifications'],
            reply_markup=buttons.yes_no(),
            parse_mode=ParseMode.HTML
        )
        await Menu.aq_set_notifications.set()
    elif message.text == language['Change']:  # Реагує на кнопку Змінити
        await message.answer(
            language['AQ Write new name'],
            reply_markup=types.ReplyKeyboardRemove(),
            parse_mode=ParseMode.HTML
        )
    elif message.text == language['Save']:  # Реагує на кнопку Зберегти
        user_data = await state.get_data()
        await message.answer(
            language['AQ Location name will be'].format(user_data['chosen_city']),
            parse_mode=ParseMode.HTML
        )
        await message.answer(
            language['AQ Turn On/Off notifications'],
            reply_markup=buttons.yes_no(),
            parse_mode=ParseMode.HTML
        )
        await Menu.aq_set_notifications.set()
    else:  # Реагує на надсилання повідомлення
        await state.update_data(chosen_city=message.text)
        await message.answer(
            language['AQ Save new location name'],
            reply_markup=buttons.aq_save_new_name(),
            parse_mode=ParseMode.HTML
        )


async def aq_set_notifications(message: types.Message, state: FSMContext):
    """Функція реагує на натискання кнопок у меню запиту Сповіщень"""
    user_data = await state.get_data()
    if message.text == language['Yes']:
        db.add_aq_location(int(message.from_user.id), int(user_data['chosen_city_idx']),
                           user_data['chosen_city'], int(user_data['chosen_city_aqi']),
                           20, True)
        await state.reset_data()
        await message.answer(
            language['AQ Menu'],
            reply_markup=buttons.aq_menu(),
            parse_mode=ParseMode.HTML
        )
        await Menu.aq_menu.set()
    elif message.text == language['No']:
        db.add_aq_location(int(message.from_user.id), int(user_data['chosen_city_idx']),
                           user_data['chosen_city'], int(user_data['chosen_city_aqi']),
                           20, False)
        await state.reset_data()
        await message.answer(
            language['AQ Menu'],
            reply_markup=buttons.aq_menu(),
            parse_mode=ParseMode.HTML
        )
        await Menu.aq_menu.set()


async def aq_select_location_by_users_location(message: types.Message, state: FSMContext):
    """Функція отримує від користувача його геолокацію, відправляє запит та відправляє результат користувачу"""
    latitude = message.location["latitude"]
    longitude = message.location["longitude"]
    await message.answer(
        language['AQ If have got your location and searching for result'],
        reply_markup=types.ReplyKeyboardRemove(),
        parse_mode=ParseMode.HTML
    )
    success, text, aqi, idx, name = aq.get_response_by_location(latitude, longitude)
    # Отримуємо {результат запиту; текст для відповіді користувачу; стан повітря; id локації; ім'я локації}
    await aq_show_response_in_adding(message, state, success, text, aqi, idx, name)


async def aq_show_response_in_adding(message, state, success, text, aqi, idx, name):
    if success:
        loc_exists, loc_name = db.aq_location_exists(message.from_user.id, int(idx))
        if not loc_exists:  # Якщо в користувача вже є ця локація
            await state.update_data(chosen_city=name)
            await state.update_data(chosen_city_idx=idx)
            await state.update_data(chosen_city_aqi=aqi)
            await message.answer(
                text,
                parse_mode=ParseMode.HTML
            )
            await message.answer(
                language['AQ Ask to add location'],
                reply_markup=buttons.yes_no(),
                parse_mode=ParseMode.HTML
            )
            await Menu.aq_show_aqi_and_ask.set()
        else:
            await message.answer(
                text,
                parse_mode=ParseMode.HTML
            )
            await message.answer(
                language['AQ You have this location'].format(loc_name),
                parse_mode=ParseMode.HTML
            )
            await message.answer(
                language['AQ Menu'],
                reply_markup=buttons.aq_menu(),
                parse_mode=ParseMode.HTML
            )
            await Menu.aq_menu.set()
    else:
        await message.answer(
            text,
            parse_mode=ParseMode.HTML
        )
        await message.answer(
            language['AQ Menu'],
            reply_markup=buttons.aq_menu(),
            parse_mode=ParseMode.HTML
        )
        await Menu.aq_menu.set()


async def aq_select_location_by_users_location_back(message: types.Message):
    """Функція реагує на кнопку Назад у меню з відправкою геолокації користувача"""
    await message.answer(
        language['AQ Add Location Menu'],
        reply_markup=buttons.aq_add_location()
    )
    await Menu.aq_add_location.set()


async def aq_my_locations_menu(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if message.text in user_data['user_locations']:
        await state.reset_data()
        location = db.aq_get_location_information(message.from_user.id, message.text)
        await state.update_data(check_location_idx=location[0][2])
        await state.update_data(check_location_name=location[0][3])
        await state.update_data(check_location_step=location[0][5])
        await state.update_data(check_location_notifications=location[0][6])
        await state.update_data(check_location_aqi=location[0][4])
        user_data = await state.get_data()
        aqi = aq.get_response_by_idx(user_data['check_location_idx'])
        if aqi != "Error":
            await state.update_data(check_location_aqi=aqi)
            user_data = await state.get_data()
            db.aq_update_aqi(message.from_user.id, int(user_data['check_location_idx']), int(aqi))

            await message.answer(
                language['AQ User Location Info'].format(message.text, user_data['check_location_aqi'],
                                                         user_data['check_location_step'],
                                                         user_data['check_location_notifications']),
                reply_markup=buttons.aq_user_location_menu(user_data['check_location_notifications'])
            )
        else:
            await message.answer(
                language['AQ User Location Info'].format(message.text, str(user_data['check_location_aqi']) + language[
                    'AQ Update Error'],
                                                         user_data['check_location_step'],
                                                         user_data['check_location_notifications']),
                reply_markup=buttons.aq_user_location_menu(user_data['check_location_notifications'])
            )
        await Menu.aq_user_location_menu.set()
    elif message.text == language['Back']:
        await message.answer(
            language['AQ Menu'],
            reply_markup=buttons.aq_menu()
        )
        await state.reset_data()
        await Menu.aq_menu.set()
    else:
        await message.answer(
            language['AQ You have no location with this name. Select from keyboard']
        )


async def aq_user_location_menu(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    # {'check_location_idx': 11662, 'check_location_name': 'Київ', 'check_location_step': 20,
    #  'check_location_notifications': False, 'check_location_aqi': 11}
    if user_data['check_location_notifications'] and message.text == language['AQ Notifications Off']:
        db.aq_update_notifications(message.from_user.id, user_data['check_location_idx'], False)
        await state.update_data(check_location_notifications=False)
        await message.answer(
            language['AQ Notifications turned off'],
            reply_markup=buttons.aq_user_location_menu(False)
        )
    elif not user_data['check_location_notifications'] and message.text == language['AQ Notifications On']:
        db.aq_update_notifications(message.from_user.id, user_data['check_location_idx'], True)
        await state.update_data(check_location_notifications=True)
        await message.answer(
            language['AQ Notifications turned on'],
            reply_markup=buttons.aq_user_location_menu(True)
        )
    elif message.text == language['AQ Edit Name']:
        await state.update_data(check_location_name_temp="123456789123456789123456789")
        await message.answer(
            language['AQ Edit name of location'],
            reply_markup=buttons.aq_edit_name(False)
        )
        await Menu.aq_edit_name.set()
    elif message.text == language['AQ Edit Step']:
        await state.update_data(check_location_step_temp="123456789123456789123456789")
        await message.answer(
            language['AQ Edit step of location'],
            reply_markup=buttons.aq_edit_step(False)
        )
        await Menu.aq_edit_step.set()
    elif message.text == language['AQ Delete location']:
        db.aq_user_delete_location(message.from_user.id, user_data['check_location_idx'])
        locations = db.aq_user_have_locations(message.from_user.id)
        if bool(len(locations)):
            names = functions.aq_get_names_from_locations_list(locations)
            await state.update_data(user_locations=names)
            await message.answer(
                language['AQ Show user locations'],
                reply_markup=buttons.aq_select_city(names)
            )
            await Menu.aq_my_locations_menu.set()
        else:
            await message.answer(
                language['AQ You have no locations'],
                reply_markup=buttons.aq_menu()
            )
    elif message.text == language['Back']:
        await state.reset_data()
        locations = db.aq_user_have_locations(message.from_user.id)
        names = functions.aq_get_names_from_locations_list(locations)
        await state.update_data(user_locations=names)
        await message.answer(
            language['AQ Show user locations'],
            reply_markup=buttons.aq_select_city(names)
        )
        await Menu.aq_my_locations_menu.set()


async def aq_edit_name(message: types.Message, state: FSMContext):
    """Функція записує нове ім'я. Тут обробка меню зі зміною імені"""
    if len(message.text) > 20:  # Довжина не має перевищувати 20 символів
        await message.answer(
            language['AQ Length limit of name'],
        )
    elif db.aq_location_name_exists(message.from_user.id, message.text):
        await message.answer(
            language['AQ Location with such name already exists'],
            reply_markup=buttons.aq_edit_name(False)
        )
    elif message.text == language['Save']:  # Реагує на кнопку Оновити
        user_data = await state.get_data()
        if user_data['check_location_name_temp'] == '123456789123456789123456789':
            await message.answer(
                language['AQ Please send new name'],
            )
        else:
            await state.update_data(check_location_name=user_data['check_location_name_temp'])
            user_data = await state.get_data()
            db.aq_update_name(message.from_user.id, user_data['check_location_idx'], user_data['check_location_name'])
            await message.answer(
                language['AQ Location name will be'].format(user_data['check_location_name']),
                parse_mode=ParseMode.HTML
            )
            await state.reset_data()
            location = db.aq_get_location_information(message.from_user.id, user_data['check_location_name'])
            await state.update_data(check_location_idx=location[0][2])
            await state.update_data(check_location_name=location[0][3])
            await state.update_data(check_location_step=location[0][5])
            await state.update_data(check_location_notifications=location[0][6])
            await state.update_data(check_location_aqi=location[0][4])
            user_data = await state.get_data()
            aqi = aq.get_response_by_idx(user_data['check_location_idx'])
            if aqi != "Error":
                await state.update_data(check_location_aqi=aqi)
                user_data = await state.get_data()
                db.aq_update_aqi(message.from_user.id, int(user_data['check_location_idx']), int(aqi))

                await message.answer(
                    language['AQ User Location Info'].format(message.text, user_data['check_location_aqi'],
                                                             user_data['check_location_step'],
                                                             user_data['check_location_notifications']),
                    reply_markup=buttons.aq_user_location_menu(user_data['check_location_notifications'])
                )
            else:
                await message.answer(
                    language['AQ User Location Info'].format(message.text,
                                                             str(user_data['check_location_aqi']) + language[
                                                                 'AQ Update Error'],
                                                             user_data['check_location_step'],
                                                             user_data['check_location_notifications']),
                    reply_markup=buttons.aq_user_location_menu(user_data['check_location_notifications'])
                )
            await Menu.aq_user_location_menu.set()
    elif message.text == language['Back']:
        user_data = await state.get_data()
        await message.answer(
            language['AQ Name did not change'],
            reply_markup=buttons.aq_user_location_menu(user_data['check_location_notifications'])
        )
        await Menu.aq_user_location_menu.set()
    else:  # Реагує на надсилання повідомлення
        await state.update_data(check_location_name_temp=message.text)
        await message.answer(
            language['AQ Save new location name'],
            reply_markup=buttons.aq_edit_name(True)
        )


async def aq_edit_step(message: types.Message, state: FSMContext):
    """Функція записує новий крок. Тут обробка меню зі зміною кроку"""
    if message.text == language['Save']:  # Реагує на кнопку Оновити
        user_data = await state.get_data()
        if user_data['check_location_step_temp'] == '123456789123456789123456789':
            await message.answer(
                language['AQ Please send new step'],
            )
        else:
            await state.update_data(check_location_step=user_data['check_location_step_temp'])
            user_data = await state.get_data()
            db.aq_update_step(message.from_user.id, user_data['check_location_idx'], user_data['check_location_step'])
            await message.answer(
                language['AQ Location step will be'].format(user_data['check_location_step']),
                parse_mode=ParseMode.HTML
            )
            await state.reset_data()
            location = db.aq_get_location_information(message.from_user.id, user_data['check_location_name'])
            await state.update_data(check_location_idx=location[0][2])
            await state.update_data(check_location_name=location[0][3])
            await state.update_data(check_location_step=location[0][5])
            await state.update_data(check_location_notifications=location[0][6])
            await state.update_data(check_location_aqi=location[0][4])
            user_data = await state.get_data()
            aqi = aq.get_response_by_idx(user_data['check_location_idx'])
            if aqi != "Error":
                await state.update_data(check_location_aqi=aqi)
                user_data = await state.get_data()
                db.aq_update_aqi(message.from_user.id, int(user_data['check_location_idx']), int(aqi))

                await message.answer(
                    language['AQ User Location Info'].format(message.text, user_data['check_location_aqi'],
                                                             user_data['check_location_step'],
                                                             user_data['check_location_notifications']),
                    reply_markup=buttons.aq_user_location_menu(user_data['check_location_notifications'])
                )
            else:
                await message.answer(
                    language['AQ User Location Info'].format(message.text,
                                                             str(user_data['check_location_aqi']) + language[
                                                                 'AQ Update Error'],
                                                             user_data['check_location_step'],
                                                             user_data['check_location_notifications']),
                    reply_markup=buttons.aq_user_location_menu(user_data['check_location_notifications'])
                )
            await Menu.aq_user_location_menu.set()
    elif message.text == language['Back']:
        user_data = await state.get_data()
        await message.answer(
            language['AQ Step did not change'],
            reply_markup=buttons.aq_user_location_menu(user_data['check_location_notifications'])
        )
        await Menu.aq_user_location_menu.set()
    else:  # Реагує на надсилання повідомлення
        if message.text.isdigit():
            if len(message.text) > 2:  # Довжина не має перевищувати 2 символа
                await message.answer(
                    language['AQ Length limit of step'],
                )
            else:
                if int(message.text) < 1:
                    await message.answer(
                        language['AQ Step must be > 0'],
                        reply_markup=buttons.aq_edit_step(True)
                    )
                else:
                    await state.update_data(check_location_step_temp=message.text)
                    await message.answer(
                        language['AQ Save new location step'],
                        reply_markup=buttons.aq_edit_step(True)
                    )
        else:
            await message.answer(
                language['AQ Send digit']
            )
# =======================================================


# ======================================= Air Temperature
async def at_menu_action(message: types.Message, state: FSMContext):
    if message.text == language['Back']:
        await message.answer(
            language['Menu'],
            reply_markup=buttons.menu()
        )
        await Menu.menu.set()
    elif message.text == language['Add Location']:
        await message.answer(
            language['AT Add Location Menu'],
            reply_markup=buttons.at_add_location()
        )
        await Menu.at_add_location.set()
    elif message.text == language['My Locations']:
        locations = db.at_user_have_locations(message.from_user.id)
        if bool(len(locations)):
            names = functions.at_get_names_from_locations_list(locations)
            await state.update_data(user_locations=names)
            await message.answer(
                language['AT Show user locations'],
                reply_markup=buttons.at_select_city(names)
            )
            await Menu.at_my_locations_menu.set()
        else:
            await message.answer(
                language['AT You have no locations']
            )
            await Menu.at_menu.set()


async def at_menu_add_location(message: types.Message):
    if message.text == language['Geolocation']:
        await message.answer(
            language['AT Share your location'],
            reply_markup=buttons.at_share_location()
        )
        await Menu.at_select_location_by_users_location.set()
    elif message.text == language['Back']:
        await message.answer(
            language['AT Menu'],
            reply_markup=buttons.at_menu()
        )
        await Menu.at_menu.set()


async def at_select_location_by_users_location(message: types.Message, state: FSMContext):
    """Функція отримує від користувача його геолокацію, відправляє запит та відправляє результат користувачу"""
    latitude = str(message.location["latitude"])[:5]
    longitude = str(message.location["longitude"])[:5]
    city, response = await at.get_response_by_location(latitude, longitude, "", False)
    await state.update_data(chosen_city_lat=latitude)
    await state.update_data(chosen_city_lon=longitude)
    await message.answer(
        language['AT If have got your location and searching for result'],
        reply_markup=types.ReplyKeyboardRemove()
    )
    if city != "Error":
        await at_show_response_in_adding(message, state, city, response)
    else:
        await message.answer(
            response
        )
        await message.answer(
            language['AT Menu'],
            reply_markup=buttons.at_menu()
        )
        await Menu.at_menu.set()


async def at_show_response_in_adding(message, state, city, response):
    await state.update_data(check_location_name=city)
    await message.answer(
        response,
        parse_mode=ParseMode.HTML
    )
    await message.answer(
        language['AT Ask to add location'],
        reply_markup=buttons.yes_no()
    )
    await Menu.at_show_temp_and_ask.set()


async def at_show_temp_and_ask(message: types.Message, state: FSMContext):
    """Т Функція реагує на натискання кнопок у меню з запитом на зберігання даної локації"""
    if message.text == language['Yes']:
        user_data = await state.get_data()
        if db.at_location_name_exists(message.from_user.id, user_data['check_location_name']):
            await state.update_data(check_location_name_temp="123456789123456789123456789")
            await message.answer(
                language['AT Name exists, change it'].format(user_data['check_location_name']),
                parse_mode=ParseMode.HTML,
                reply_markup=types.ReplyKeyboardRemove()
            )
            await Menu.at_set_location_name.set()
        else:
            await message.answer(
                language['AT Do you want to change name'].format(user_data['check_location_name']),
                parse_mode=ParseMode.HTML,
                reply_markup=buttons.yes_no()
            )
            await Menu.at_ask_to_change_name.set()
    elif message.text == language['No']:
        await message.answer(
            language['AT Menu'],
            reply_markup=buttons.at_menu()
        )
        await Menu.at_menu.set()


async def at_set_location_name(message: types.Message, state: FSMContext):
    """Функція реагує на натискання кнопок та надсилання слів у меню Обов'язкової заміни імені локації"""
    if len(message.text) > 20:  # Довжина не має перевищувати 20 символів
        await message.answer(
            language['AT Length limit of name'],
        )
    elif db.at_location_name_exists(message.from_user.id, message.text):
        await message.answer(
            language['AT Location with such name already exists']
        )
    elif message.text == language['Save']:  # Реагує на кнопку Зберегти
        user_data = await state.get_data()
        if user_data['check_location_name_temp'] == '123456789123456789123456789':
            await message.answer(
                language['AT Please send new name'],
                parse_mode=ParseMode.HTML,
                reply_markup=types.ReplyKeyboardRemove()
            )
        else:
            user_data = await state.get_data()
            await state.update_data(check_location_name=user_data['check_location_name_temp'])
            await message.answer(
                language['AT Location name will be'].format(user_data['check_location_name_temp']),
                parse_mode=ParseMode.HTML
            )
            await message.answer(
                language['AT Turn On/Off notifications'],
                parse_mode=ParseMode.HTML,
                reply_markup=buttons.yes_no()
            )
            await Menu.at_set_notifications.set()
    else:  # Реагує на надсилання повідомлення
        await state.update_data(check_location_name_temp=message.text)
        await message.answer(
            language['AT Save new location name'],
            reply_markup=buttons.at_save_new_name()
        )


async def at_ask_to_change_name(message: types.Message, state: FSMContext):
    """Т Функція реагує на натискання кнопок у меню з запитом на зміну імені локації"""
    if message.text == language['Yes']:
        await state.update_data(check_location_name_temp="123456789123456789123456789")
        await message.answer(
            language['AT Ok, write new name for this location'],
            parse_mode=ParseMode.HTML,
            reply_markup=types.ReplyKeyboardRemove()
        )
        await Menu.at_change_location_name.set()
    elif message.text == language['No']:
        user_data = await state.get_data()
        await message.answer(
            language['AT Ok, name will be'].format(user_data['check_location_name']),
            parse_mode=ParseMode.HTML,
            reply_markup=types.ReplyKeyboardRemove()
        )
        await message.answer(
            language['AT Turn On/Off notifications'],
            reply_markup=buttons.yes_no()
        )
        await Menu.at_set_notifications.set()


async def at_change_location_name(message: types.Message, state: FSMContext):
    """Функція записує нове ім'я. Тут обробка меню зі зміною імені"""
    if len(message.text) > 20:  # Довжина не має перевищувати 20 символів
        await message.answer(
            language['AT Length limit of name'],
        )
    elif db.aq_location_name_exists(message.from_user.id, message.text):
        await message.answer(
            language['AT Location with such name already exists'],
            reply_markup=buttons.aq_edit_name(False)
        )
    elif message.text == language['Save']:  # Реагує на кнопку берегти
        user_data = await state.get_data()
        if user_data['check_location_name_temp'] == '123456789123456789123456789':
            await message.answer(
                language['AT Please send new name'],
                reply_markup=types.ReplyKeyboardRemove()
            )
        else:
            await state.update_data(check_location_name=user_data['check_location_name_temp'])
            # state.reset_data()
            user_data = await state.get_data()
            await message.answer(
                language['AT Ok, name will be'].format(user_data['check_location_name']),
                parse_mode=ParseMode.HTML,
                reply_markup=types.ReplyKeyboardRemove()
            )
            await message.answer(
                language['AT Turn On/Off notifications'],
                reply_markup=buttons.yes_no()
            )
            await Menu.at_set_notifications.set()
    # elif message.text == language['Back']:
    #     user_data = await state.get_data()
    #     await message.answer(
    #         language['AQ Name did not change'],
    #         reply_markup=buttons.aq_user_location_menu(user_data['check_location_notifications'])
    #     )
    #     await Menu.aq_user_location_menu.set()
    else:  # Реагує на надсилання повідомлення
        await state.update_data(check_location_name_temp=message.text)
        await message.answer(
            language['AT Save new location name'],
            reply_markup=buttons.at_edit_name(True)
        )


async def at_set_notifications(message: types.Message, state: FSMContext):
    """Т Функція реагує на натискання кнопок у меню запиту Сповіщень"""
    user_data = await state.get_data()
    if message.text == language['Yes']:
        db.add_at_location(int(message.from_user.id), str(user_data['check_location_name']),
                           str(user_data['chosen_city_lat']), str(user_data['chosen_city_lon']), True)
        await state.reset_data()
        await message.answer(
            language['AT Menu'],
            reply_markup=buttons.at_menu()
        )
        await Menu.at_menu.set()
    elif message.text == language['No']:
        db.add_at_location(int(message.from_user.id), str(user_data['check_location_name']),
                           str(user_data['chosen_city_lat']), str(user_data['chosen_city_lon']), False)
        await state.reset_data()
        await message.answer(
            language['AT Menu'],
            reply_markup=buttons.at_menu()
        )
        await Menu.at_menu.set()



async def at_my_locations_menu(message: types.Message, state: FSMContext):
    """Т Меню локацій користувача"""
    user_data = await state.get_data()
    if message.text in user_data['user_locations']:
        await state.reset_data()
        location = db.at_get_location_information(message.from_user.id, message.text)
        await state.update_data(check_location_name=location[0][5])
        await state.update_data(check_location_notifications=location[0][4])
        await state.update_data(check_location_lat=location[0][3])
        await state.update_data(check_location_lon=location[0][2])

        user_data = await state.get_data()

        latitude = str(user_data['check_location_lat'])
        longitude = str(user_data['check_location_lon'])
        city, response = await at.get_response_by_location(latitude, longitude, user_data['check_location_name'], True)

        if city != "Error":
            await message.answer(
                response,
                parse_mode=ParseMode.HTML
            )
            await message.answer(
                language['AT Settings'],
                reply_markup=buttons.at_user_location_menu(user_data['check_location_notifications'])
            )
            await Menu.at_user_location_menu.set()
        else:
            await message.answer(
                response
            )
    elif message.text == language['Back']:
        await message.answer(
            language['AT Menu'],
            reply_markup=buttons.at_menu()
        )
        await Menu.at_menu.set()
        await state.reset_data()
    else:
        await message.answer(
            language['AT You have no location with this name. Select from keyboard']
        )


async def at_user_location_menu(message: types.Message, state: FSMContext):
    """Меню налаштувань локації користувача"""
    user_data = await state.get_data()
    if user_data['check_location_notifications'] and message.text == language['AT Notifications Off']:
        db.at_update_notifications(message.from_user.id, user_data['check_location_name'], False)
        await state.update_data(check_location_notifications=False)
        await message.answer(
            language['AT Notifications turned off'],
            reply_markup=buttons.at_user_location_menu(False)
        )
    elif not user_data['check_location_notifications'] and message.text == language['AT Notifications On']:
        db.at_update_notifications(message.from_user.id, user_data['check_location_name'], True)
        await state.update_data(check_location_notifications=True)
        await message.answer(
            language['AT Notifications turned on'],
            reply_markup=buttons.at_user_location_menu(True)
        )
    elif message.text == language['AT Edit Name']:
        await state.update_data(check_location_name_temp="123456789123456789123456789")
        await message.answer(
            language['AT Edit name of location'],
            reply_markup=buttons.at_set_new_name(False)
        )
        await Menu.at_edit_name.set()
    elif message.text == language['AT Delete location']:
        db.at_user_delete_location(message.from_user.id, user_data['check_location_name'])
        locations = db.at_user_have_locations(message.from_user.id)

        if bool(len(locations)):
            names = functions.at_get_names_from_locations_list(locations)
            await state.update_data(user_locations=names)
            await message.answer(
                language['AT Show user locations'],
                reply_markup=buttons.at_select_city(names)
            )
            await Menu.at_my_locations_menu.set()
        else:
            await message.answer(
                language['AT You have no locations'],
                reply_markup=buttons.at_menu()
            )
            await Menu.at_menu.set()
    elif message.text == language['Back']:
        await state.reset_data()
        locations = db.at_user_have_locations(message.from_user.id)
        names = functions.at_get_names_from_locations_list(locations)
        await state.update_data(user_locations=names)
        await message.answer(
            language['AT Show user locations'],
            reply_markup=buttons.at_select_city(names)
        )
        await Menu.at_my_locations_menu.set()


async def at_edit_name(message: types.Message, state: FSMContext):
    """Функція записує нове ім'я. Тут обробка меню зі зміною імені"""
    if len(message.text) > 20:  # Довжина не має перевищувати 20 символів
        await message.answer(
            language['AT Length limit of name'],
        )
    elif db.at_location_name_exists(message.from_user.id, message.text):
        await message.answer(
            language['AT Location with such name already exists'],
            reply_markup=buttons.at_set_new_name(False)
        )
    elif message.text == language['Save']:  # Реагує на кнопку Оновити
        user_data = await state.get_data()
        if user_data['check_location_name_temp'] == '123456789123456789123456789':
            await message.answer(
                language['AT Please send new name'],
            )
        else:
            await state.update_data(check_location_name=user_data['check_location_name_temp'])
            user_data = await state.get_data()
            await message.answer(
                language['AT Ok, name will be'].format(user_data['check_location_name']),
                parse_mode=ParseMode.HTML,
                reply_markup=buttons.at_user_location_menu(user_data['check_location_notifications'])
            )
            await Menu.at_user_location_menu.set()
    elif message.text == language['Back']:
        user_data = await state.get_data()
        await message.answer(
            language['AT Name did not change'],
            reply_markup=buttons.at_user_location_menu(user_data['check_location_notifications'])
        )
        await Menu.at_user_location_menu.set()
    else:  # Реагує на надсилання повідомлення
        await state.update_data(check_location_name_temp=message.text)
        await message.answer(
            language['AT Save new location name'],
            reply_markup=buttons.at_set_new_name(True)
        )
# =======================================================

# async def cmd_cancel(message: types.Message, state: FSMContext):
#     await state.finish()
#     await message.answer("Действие отменено", reply_markup=types.ReplyKeyboardRemove())


# async def secret_command(message: types.Message):
#     await message.answer("Поздравляю! Эта команда доступна только администратору бота.")


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state="*")  # start
    dp.register_message_handler(menu, state=Menu.instructions)              # реагує на кнопку "Прочитав інструкцію"
    dp.register_message_handler(menu_action, state=Menu.menu)               # реагує на Головне Меню
    dp.register_message_handler(aq_menu_action, state=Menu.aq_menu)         # ЯП реагує на меню Якості Повітря
    dp.register_message_handler(at_menu_action, state=Menu.at_menu)         # ТП реагує на меню Температури Повітря
    dp.register_message_handler(aq_menu_add_location,
                                state=Menu.aq_add_location)                 # ЯП реагує на меню додавання нової локації
    dp.register_message_handler(aq_select_location_city_by_name,
                                state=Menu.aq_select_location_city_by_name)     # ЯП реагує на натискання кнопок меню зі списком міст
    dp.register_message_handler(aq_show_aqi_and_ask,
                                state=Menu.aq_show_aqi_and_ask)                 # ЯП реакція на відповідь на запитання "Чи зберігати локацію"
    dp.register_message_handler(aq_set_location_name,
                                state=Menu.aq_set_location_name)                # ЯП реагує на події при обранні назви локації
    dp.register_message_handler(aq_set_notifications,
                                state=Menu.aq_set_notifications)                # ЯП реагує на відповідь на запитання про Сповіщення
    dp.register_message_handler(aq_select_location_by_users_location, state=Menu.aq_select_location_by_users_location,
                                content_types=["location"])                     # ЯП реагує на отримання Геолокації
    dp.register_message_handler(aq_select_location_by_users_location_back,
                                state=Menu.aq_select_location_by_users_location)    # ЯП реагує на кнопку у меню з надсиланням Геолокації
    dp.register_message_handler(aq_my_locations_menu,
                                state=Menu.aq_my_locations_menu)                    # ЯП Реагує на кнопки у меню Мої локації
    dp.register_message_handler(aq_user_location_menu,
                                state=Menu.aq_user_location_menu)                   # ЯП Реагує на кнопки у меню локації користувача
    dp.register_message_handler(aq_edit_name,
                                state=Menu.aq_edit_name)                    # ЯП Реагує на кнопки у меню оновлення імені локації
    dp.register_message_handler(aq_edit_step, state=Menu.aq_edit_step)      # ЯП Реагує на кнопки у меню оновлення імені локації

    dp.register_message_handler(at_menu_add_location, state=Menu.at_add_location)       # Т реагує на меню додавання нової локації
    dp.register_message_handler(at_select_location_by_users_location, state=Menu.at_select_location_by_users_location, content_types=["location"])      # Т реагує на отримання Геолокації
    dp.register_message_handler(at_show_temp_and_ask, state=Menu.at_show_temp_and_ask)  # Т реагує на запит збереження локації (nache)
    dp.register_message_handler(at_set_location_name, state=Menu.at_set_location_name)  # T реагує на події при обранні назви локації
    dp.register_message_handler(at_set_notifications, state=Menu.at_set_notifications)  # T реагує на події при підключенні сповіщень
    dp.register_message_handler(at_ask_to_change_name, state=Menu.at_ask_to_change_name)  # T реагує на питання про зміну назви локації
    dp.register_message_handler(at_change_location_name, state=Menu.at_change_location_name)  # T реагує на зміни назви локації
    dp.register_message_handler(at_my_locations_menu, state=Menu.at_my_locations_menu)  # T меню з локаціями користувача
    dp.register_message_handler(at_user_location_menu, state=Menu.at_user_location_menu)  # T меню налаштувань локації користувача
    dp.register_message_handler(at_edit_name, state=Menu.at_edit_name)  # T реагує на зміну назви локації
    # dp.register_message_handler(cmd_cancel, Text(equals="отмена", ignore_case=True), state="*")
    # dp.register_message_handler(secret_command, IDFilter(user_id=admin_id), commands="abracadabra")
