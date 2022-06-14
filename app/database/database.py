import os
import psycopg2
from app.config_reader import load_config


# 409486672 Me
# 168691139 Demk
# idx   name  last_aqi step notification
# 11663 КНК   77       10   true
# 11871 Львів 63       20   true
# 8121  Łód   8        20   true


class PostgreSQLDataBase:
    def __init__(self):
        """Встановлює зв'язок з базою даних"""
        config = load_config("config/bot.ini")
        self.connection = psycopg2.connect(database=config.tg_bot.db_name, user=config.tg_bot.db_user,
                                           password=config.tg_bot.db_pass, host=config.tg_bot.db_host,
                                           port=config.tg_bot.db_port)
        self.cursor = self.connection.cursor()


    def get_all_users(self):
        """Повертає список користувачів"""
        with self.connection:
            self.cursor.execute("SELECT user_id FROM users")
            result = self.cursor.fetchall()
            return result


    def user_exists(self, user_id):
        """Перевіряє на наявність даного користувача"""
        with self.connection:
            self.cursor.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
            result = self.cursor.fetchall()
            return bool(len(result))

    def add_user(self, user_id):
        """Додає користувача"""
        with self.connection:
            return self.cursor.execute("INSERT INTO users (user_id) VALUES (%s)", (user_id,))

    def add_aq_location(self, user_id, idx, name, last_aqi, step, notification):
        """Додає локацію"""
        with self.connection:
            return self.cursor.execute("INSERT INTO locations_air_quality "
                                       "(user_id, idx, name, last_aqi, step, notification) "
                                       "VALUES (%s, %s, %s, %s, %s, %s)",
                                       (user_id, idx, name, last_aqi, step, notification))

    def aq_location_exists(self, user_id, idx):
        """Перевіряє на наявність в даного користувача даної локації"""
        with self.connection:
            self.cursor.execute("SELECT * FROM locations_air_quality WHERE user_id = %s and idx = %s", (user_id, idx))
            result = self.cursor.fetchall()
            if bool(len(result)):
                return True, result[0][3]
            else:
                return False, "NoData"

    def aq_location_name_exists(self, user_id, name):
        """Перевіряє на наявність в даного користувача локації з таким іменем"""
        with self.connection:
            self.cursor.execute("SELECT * FROM locations_air_quality WHERE user_id = %s and name = %s", (user_id, name))
            result = self.cursor.fetchall()
            return bool(len(result))

    def aq_user_have_locations(self, user_id):
        """Повертає список локацій користувача"""
        with self.connection:
            self.cursor.execute("SELECT * FROM locations_air_quality WHERE user_id = %s", (user_id,))
            result = self.cursor.fetchall()
            return result

    def aq_get_location_information(self, user_id, name):
        """Повертає список локацію користувача"""
        with self.connection:
            self.cursor.execute("SELECT * FROM locations_air_quality WHERE user_id = %s and name = %s", (user_id, name))
            result = self.cursor.fetchall()
            return result

    def aq_update_aqi(self, user_id, idx, aqi):
        """Оновлює останній AQI локації користувача"""
        with self.connection:
            return self.cursor.execute("UPDATE locations_air_quality SET last_aqi = %s WHERE user_id = %s and idx = %s",
                                       (aqi, user_id, idx))

    def aq_update_notifications(self, user_id, idx, notifications):
        """Оновлює сповіщення локації користувача"""
        with self.connection:
            return self.cursor.execute(
                "UPDATE locations_air_quality SET notification = %s WHERE user_id = %s and idx = %s",
                (notifications, user_id, idx))

    def aq_update_name(self, user_id, idx, name):
        """Оновлює ім'я локації користувача"""
        with self.connection:
            return self.cursor.execute("UPDATE locations_air_quality SET name = %s WHERE user_id = %s and idx = %s",
                                       (name, user_id, idx))

    def aq_update_step(self, user_id, idx, step):
        """Оновлює крок локації користувача"""
        with self.connection:
            return self.cursor.execute("UPDATE locations_air_quality SET step = %s WHERE user_id = %s and idx = %s",
                                       (step, user_id, idx))

    def aq_user_delete_location(self, user_id, idx):
        """Видаляє локацію користувача"""
        with self.connection:
            return self.cursor.execute("DELETE FROM locations_air_quality WHERE user_id = %s and idx = %s",
                                       (user_id, idx))



    def at_location_name_exists(self, user_id, name):
        """Т Перевіряє на наявність в даного користувача локації з таким іменем"""
        with self.connection:
            self.cursor.execute("SELECT * FROM locations_air_temperature WHERE user_id = %s and name = %s",
                                (user_id, name))
            result = self.cursor.fetchall()
            return bool(len(result))

    def add_at_location(self, user_id, name, lat, lon, notification):
        """Додає локацію"""
        with self.connection:
            return self.cursor.execute("INSERT INTO locations_air_temperature (user_id, lon, lat, notification, name)  VALUES (%s, %s, %s, %s, %s)",
                                       (user_id, lon, lat, notification, name))

    def at_user_have_locations(self, user_id):
        """Т Повертає список локацій користувача"""
        with self.connection:
            self.cursor.execute("SELECT * FROM locations_air_temperature WHERE user_id = %s", (user_id,))
            result = self.cursor.fetchall()
            return result

    def at_get_location_information(self, user_id, name):
        """Т Повертає список локацію користувача"""
        with self.connection:
            self.cursor.execute("SELECT * FROM locations_air_temperature WHERE user_id = %s and name = %s", (user_id, name))
            result = self.cursor.fetchall()
            return result

    def at_update_notifications(self, user_id, name, notifications):
        """T Оновлює сповіщення локації користувача"""
        with self.connection:
            return self.cursor.execute(
                "UPDATE locations_air_temperature SET notification = %s WHERE user_id = %s and name = %s",
                (notifications, user_id, name))

    def at_user_delete_location(self, user_id, name):
        """Видаляє локацію користувача"""
        with self.connection:
            return self.cursor.execute("DELETE FROM locations_air_temperature WHERE user_id = %s and name = %s",
                                       (user_id, name))
