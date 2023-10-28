import sys
from threading import Lock

import logging
import yaml

DTF = '%Y-%m-%d %H:%M:%S'
LOGGING_FORMAT = '%(asctime)s %(levelname)s [%(threadName)s] %(filename)s.%(funcName)s(%(lineno)d): %(message)s'
FORMATTER = logging.Formatter(LOGGING_FORMAT, DTF, style='%')

LOGGER = logging.getLogger()


class SingletonMeta(type):
    """Singleton meta class
    """
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            # another thread may succeed with the previous check again here
            with cls._lock:
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]


class ConfigLoader(metaclass=SingletonMeta):
    """Class for loading config
    """

    def __init__(self, filepath=None):
        self.loaded = None
        self.config = None
        if filepath is not None:
            self.filepath = filepath
            self.load()

    def load(self):
        try:
            if self.filepath is not None and not self.loaded:
                LOGGER.info("Loading configuration from file '{}'...".format(self.filepath))
                with open(self.filepath, 'r') as file:
                    data = file.read()
                    self.config = yaml.load(data, Loader=yaml.Loader)
                    self.loaded = True
                    LOGGER.debug("Configuration loaded.")
        except Exception as e:
            LOGGER.error(e)
            sys.exit(-1)
        return self.config

    def save(self):
        try:
            if self.filepath is not None:
                LOGGER.info("Saving configuration...")
                with open(self.filepath, 'w') as file:
                    data = yaml.dump(self.config, Dumper=yaml.Dumper)
                    file.write(data)
                LOGGER.debug("Saving configuration to file completed.")
        except Exception as e:
            LOGGER.error(e)
