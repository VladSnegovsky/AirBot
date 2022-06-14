from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

from app.language import text as language


def choose_language():
    btn_ukrainian = KeyboardButton("Українська")
    # btn_english = KeyboardButton("English󠁧󠁢󠁥󠁮󠁧󠁿")
    return ReplyKeyboardMarkup(resize_keyboard=True).add(btn_ukrainian)


def ok_button():
    btn_ok = KeyboardButton(language['Ok'])
    return ReplyKeyboardMarkup(resize_keyboard=True).add(btn_ok)


def menu():
    btn_air_quality = KeyboardButton(language['Air Quality'])
    btn_air_temperature = KeyboardButton(language['Air Temperature'])
    btn_about_this_bot = KeyboardButton(language['About This Bot'])
    return ReplyKeyboardMarkup(resize_keyboard=True).add(btn_air_quality, btn_air_temperature).add(btn_about_this_bot)


def air_temperature_menu():
    btn_test = KeyboardButton("Test T")
    btn_back = KeyboardButton(language['Back'])
    return ReplyKeyboardMarkup(resize_keyboard=True).add(btn_test, btn_back)


# ============================================= Air Quality
def aq_menu():
    btn_add_location = KeyboardButton(language['Add Location'])
    btn_my_locations = KeyboardButton(language['My Locations'])
    btn_back = KeyboardButton(language['Back'])
    return ReplyKeyboardMarkup(resize_keyboard=True).add(btn_add_location, btn_my_locations).add(btn_back)


def aq_add_location():
    btn_select_from_list = KeyboardButton(language['Select From List'])
    btn_geolocation = KeyboardButton(language['Geolocation'])
    btn_back = KeyboardButton(language['Back'])
    return ReplyKeyboardMarkup(resize_keyboard=True).add(btn_select_from_list, btn_geolocation).add(btn_back)


def aq_select_city(cities):
    btn_back = KeyboardButton(language['Back'])
    return ReplyKeyboardMarkup(resize_keyboard=True).add(*cities, btn_back)


def yes_no():
    btn_yes = KeyboardButton(language['Yes'])
    btn_no = KeyboardButton(language['No'])
    return ReplyKeyboardMarkup(resize_keyboard=True).add(btn_yes, btn_no)


def aq_set_name_for_location():
    btn_ok = KeyboardButton(language['Ok'])
    btn_change = KeyboardButton(language['Change'])
    return ReplyKeyboardMarkup(resize_keyboard=True).add(btn_ok, btn_change)


def aq_save_new_name():
    btn_save = KeyboardButton(language['Save'])
    return ReplyKeyboardMarkup(resize_keyboard=True).add(btn_save)


def aq_share_location():
    btn_my_location = KeyboardButton(language['AQ My location'], request_location=True)
    btn_back = KeyboardButton(language['Back'])
    return ReplyKeyboardMarkup(resize_keyboard=True).add(btn_my_location).add(btn_back)


def aq_user_location_menu(notification):
    btn_edit_name = KeyboardButton(language['AQ Edit Name'])
    btn_edit_step = KeyboardButton(language['AQ Edit Step'])
    if notification:
        btn_notifications = KeyboardButton(language['AQ Notifications Off'])
    else:
        btn_notifications = KeyboardButton(language['AQ Notifications On'])
    btn_delete_location = KeyboardButton(language['AQ Delete location'])
    btn_back = KeyboardButton(language['Back'])
    return ReplyKeyboardMarkup(resize_keyboard=True).add(btn_edit_name, btn_edit_step).add(btn_notifications, btn_delete_location).add(btn_back)


def aq_edit_name(update):
    btn_back = KeyboardButton(language['Back'])
    if update:
        btn_update = KeyboardButton(language['Save'])
        return ReplyKeyboardMarkup(resize_keyboard=True).add(btn_update, btn_back)
    else:
        return ReplyKeyboardMarkup(resize_keyboard=True).add(btn_back)


def aq_edit_step(update):
    btn_back = KeyboardButton(language['Back'])
    if update:
        btn_update = KeyboardButton(language['Save'])
        return ReplyKeyboardMarkup(resize_keyboard=True).add(btn_update, btn_back)
    else:
        return ReplyKeyboardMarkup(resize_keyboard=True).add(btn_back)
# =========================================================


# ============================================= Air Temperature
def at_menu():
    btn_add_location = KeyboardButton(language['Add Location'])
    btn_my_locations = KeyboardButton(language['My Locations'])
    btn_back = KeyboardButton(language['Back'])
    return ReplyKeyboardMarkup(resize_keyboard=True).add(btn_add_location, btn_my_locations).add(btn_back)


def at_add_location():
    btn_geolocation = KeyboardButton(language['Geolocation'])
    btn_back = KeyboardButton(language['Back'])
    return ReplyKeyboardMarkup(resize_keyboard=True).add(btn_geolocation).add(btn_back)


def at_share_location():
    btn_my_location = KeyboardButton(language['AT My location'], request_location=True)
    btn_back = KeyboardButton(language['Back'])
    return ReplyKeyboardMarkup(resize_keyboard=True).add(btn_my_location).add(btn_back)


def at_set_name_for_location(back):
    if back:
        pass
    else:
        btn_save = KeyboardButton(language['Save'])
        return ReplyKeyboardMarkup(resize_keyboard=True).add(btn_save)


def at_save_new_name():
    btn_save = KeyboardButton(language['Save'])
    return ReplyKeyboardMarkup(resize_keyboard=True).add(btn_save)


def at_edit_name(update):
    if update:
        btn_update = KeyboardButton(language['Save'])
        return ReplyKeyboardMarkup(resize_keyboard=True).add(btn_update)


def at_set_new_name(update):
    btn_back = KeyboardButton(language['Back'])
    if update:
        btn_update = KeyboardButton(language['Save'])
        return ReplyKeyboardMarkup(resize_keyboard=True).add(btn_update, btn_back)
    else:
        return ReplyKeyboardMarkup(resize_keyboard=True).add(btn_back)


def at_select_city(locations):
    btn_back = KeyboardButton(language['Back'])
    return ReplyKeyboardMarkup(resize_keyboard=True).add(*locations, btn_back)


def at_user_location_menu(notification):
    btn_edit_name = KeyboardButton(language['AT Edit Name'])
    if notification:
        btn_notifications = KeyboardButton(language['AT Notifications Off'])
    else:
        btn_notifications = KeyboardButton(language['AT Notifications On'])
    btn_delete_location = KeyboardButton(language['AT Delete location'])
    btn_back = KeyboardButton(language['Back'])
    return ReplyKeyboardMarkup(resize_keyboard=True).add(btn_edit_name, btn_notifications).add(btn_delete_location).add(btn_back)
# =========================================================
