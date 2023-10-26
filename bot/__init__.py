import logging.handlers
import os
import sys
from pathlib import Path

import core
from core.config import ConfigLoader
from core.log import LOGGING_FORMAT, FORMATTER

# Basic app info
APP_NAME = "EVECommissarBot"
APP_DESCRIPTION = '''EVECommissarBot is a simple bot.
'''
APP_VERSION = '0.0.1'

# paths
ROOT_DIR_PATH = Path(__file__).parents[1]
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
     # level=log.INFO,
     level=logging.DEBUG,
     handlers=[
         HANDLER,
         logging.StreamHandler(sys.stdout)
     ]
 )

core.LOGGER = logging.getLogger()
cl = ConfigLoader(CONFIG_FILEPATH)
