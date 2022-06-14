import configparser
from dataclasses import dataclass


@dataclass
class TgBot:
    token: str
    aq_token: str
    at_token: str
    db_name: str
    db_user: str
    db_pass: str
    db_host: str
    db_port: str


@dataclass
class Config:
    tg_bot: TgBot


def load_config(path: str):
    config = configparser.ConfigParser()
    config.read(path)

    tg_bot = config["tg_bot"]

    return Config(
        tg_bot=TgBot(
            token=tg_bot["token"],
            aq_token=tg_bot["aq_token"],
            at_token=tg_bot["at_token"],
            db_name=tg_bot["db_name"],
            db_user=tg_bot["db_user"],
            db_pass=tg_bot["db_pass"],
            db_host=tg_bot["db_host"],
            db_port=tg_bot["db_port"]
        )
    )
