import logging.handlers
import os
import sys

PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'server.log')

SERVER_FORMATTER = logging.Formatter('%(asctime)s - %(levelname)-8s - %(message)s')

STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setFormatter(SERVER_FORMATTER)
STREAM_HANDLER.setLevel(logging.ERROR)

FILE_HANDLER = logging.handlers.TimedRotatingFileHandler(PATH, encoding='utf-8', interval=1, when='D')
FILE_HANDLER.setFormatter(SERVER_FORMATTER)

LOGGER = logging.getLogger('server')
LOGGER.addHandler(STREAM_HANDLER)
LOGGER.addHandler(FILE_HANDLER)
LOGGER.setLevel(logging.DEBUG)

if __name__ == '__main__':
    LOGGER.debug('Отладочная информация')
    LOGGER.info('Информационное сообщение')
    LOGGER.warning('Предупреждение')
    LOGGER.error('Ошибка')
    LOGGER.critical('Критическое сообщение')
