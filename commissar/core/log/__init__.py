import logging

DTF = '%Y-%m-%d %H:%M:%S'
LOGGING_FORMAT = '%(asctime)s %(levelname)s [%(threadName)s] %(filename)s.%(funcName)s(%(lineno)d): %(message)s'
FORMATTER = logging.Formatter(LOGGING_FORMAT, DTF, style='%')

LOGGER = logging.getLogger()
