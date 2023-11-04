import logging.handlers
import os
import pathlib
import sys
from enum import StrEnum

from commissar import core
from commissar import ConfigLoader
from commissar import FORMATTER, LOGGING_FORMAT

# info
APP_NAME = "EVECommissarApp"
APP_DESCRIPTION = '''EVECommissarApp is a simple flask application.
'''
APP_VERSION = '0.0.1'

# paths
ROOT_DIR_PATH = pathlib.Path.cwd()
LOG_DIR_PATH = os.path.join(ROOT_DIR_PATH, 'logs')
CFG_DIR_PATH = os.path.join(ROOT_DIR_PATH, 'config')
CONFIG_FILENAME = 'app_config.yml'
CONFIG_FILEPATH = os.path.join(CFG_DIR_PATH, CONFIG_FILENAME)

if not os.path.exists(LOG_DIR_PATH):
    os.makedirs(LOG_DIR_PATH)

HANDLER = logging.handlers.RotatingFileHandler(
    filename=os.path.join(LOG_DIR_PATH, APP_NAME + '.log'),
    encoding='utf-8',
    maxBytes=5 * 1024 * 1024,
    backupCount=3,
)
HANDLER.setFormatter(FORMATTER)

logging.basicConfig(
    format=LOGGING_FORMAT,
    encoding='utf-8',
    level=logging.INFO,
    # level=logging.DEBUG,
    handlers=[
        HANDLER,
        logging.StreamHandler(sys.stdout)
    ]
)

core.LOGGER = logging.getLogger("logger")
cl = ConfigLoader(CONFIG_FILEPATH)


class AppException(Exception):

    def __init__(self, http_status_code: int, error_code: int, error_message: str):
        self.http_status_code = http_status_code
        self.error_code = error_code
        self.error_message = error_message
        super().__init__(error_message)


class Result(StrEnum):
    REGISTERED = "REGISTERED"
    OK = "OK"
    FAIL = "FAIL"


class Locale(StrEnum):
    ru = "ru"
    en_US = "en_US"


SOMETHING_WENT_WRONG = {
    Locale.en_US.__str__(): "Something went wrong.",
    Locale.ru.__str__(): "Что-то пошло не так."
}

CHARACTER_ALREADY_REGISTERED = {
    Locale.en_US.__str__(): "Character has been registered already.",
    Locale.ru.__str__(): "Персонаж уже зарегистрирован"
}

CHARACTER_REGISTERED_SUCCESSFULLY = {
    Locale.en_US.__str__(): "Character registered successfully. You can close this page and return to Discord server.",
    Locale.ru.__str__(): "Персонаж успешно зарегистрирован. Вы можете закрыть эту вкладку и вернуться в Discord."
}


def get_localized(a: dict, locale: str):
    return a[locale] if locale in [Locale.ru] else a[Locale.en_US.__str__()]
