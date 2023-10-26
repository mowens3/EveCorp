import logging.handlers
import os
import sys
from pathlib import Path

import commissar_core
from commissar_core.config import ConfigLoader
from commissar_core.log import FORMATTER, LOGGING_FORMAT

# info
APP_NAME = "EVECommissarApp"
APP_DESCRIPTION = '''EVECommissarApp is a simple flask application.
'''
APP_VERSION = '0.0.1'

# paths
ROOT_DIR_PATH = Path(__file__).parents[1]
LOG_DIR_PATH = os.path.join(ROOT_DIR_PATH, 'logs')
CFG_DIR_PATH = os.path.join(ROOT_DIR_PATH, 'config')
CONFIG_FILENAME = 'app_config.yml'
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

commissar_core.LOGGER = logging.getLogger("logger")
cl = ConfigLoader(CONFIG_FILEPATH)


class ErrorWithCode(Exception):
    """Application exception with error code
    """

    def __init__(self, http_status_code: int, error_code: int, error_message: str):
        self.http_status_code = http_status_code
        self.error_code = error_code
        super().__init__(error_message)

