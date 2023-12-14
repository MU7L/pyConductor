# TODO: 每次生成两份文件

import logging
from datetime import datetime
from os import path

from settings import LOG_PATH

formatter = logging.Formatter(
    fmt='%(levelname)s[%(asctime)s]\t%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)

filename = path.join(LOG_PATH, f'{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.log')
file_handler = logging.FileHandler(filename=filename, mode='w')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)
logger.addHandler(file_handler)
