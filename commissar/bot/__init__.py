import logging.handlers
import os
import pathlib
import sys

from commissar import core
from commissar import ConfigLoader
from commissar import FORMATTER, LOGGING_FORMAT

# info
APP_NAME = "EVECommissarBot"
APP_DESCRIPTION = '''EVECommissarApp is a simple Discord Bot.
'''
APP_VERSION = '0.0.1'

# paths
ROOT_DIR_PATH = pathlib.Path.cwd()
LOG_DIR_PATH = os.path.join(ROOT_DIR_PATH, 'logs')
CFG_DIR_PATH = os.path.join(ROOT_DIR_PATH, 'config')
CONFIG_FILENAME = 'bot_config.yml'
CONFIG_FILEPATH = os.path.join(CFG_DIR_PATH, CONFIG_FILENAME)

if not os.path.exists(LOG_DIR_PATH):
    os.makedirs(LOG_DIR_PATH)

HANDLER = logging.handlers.RotatingFileHandler(
    filename=os.path.join(LOG_DIR_PATH, APP_NAME + '.log'),
    encoding='utf-8',
    maxBytes=10 * 1024 * 1024,
    backupCount=3,
)
HANDLER.setFormatter(FORMATTER)

logging.basicConfig(
    format=LOGGING_FORMAT,
    encoding='utf-8',
    # level=logging.INFO,
    level=logging.DEBUG,
    handlers=[
        HANDLER,
        logging.StreamHandler(sys.stdout)
    ]
)

core.LOGGER = logging.getLogger("logger")
cl = ConfigLoader(CONFIG_FILEPATH)

ZKILLBOARD_CHARACTER_URL_PATTERN = "https://zkillboard.com/character/{}/"
ZKILLBOARD_CORPORATION_URL_PATTERN = "https://zkillboard.com/corporation/{}/"


class BotException(Exception):
    def __init__(self, message):
        super().__init__(message)

