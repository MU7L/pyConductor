import logging
import os
import datetime

log_path = 'logs'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('[%(asctime)s %(name)s %(levelname)s]\t %(message)s')

# 控制台输出
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

# 文件输出
fh_info = logging.FileHandler(os.path.join(log_path, 'app.log'))
fh_info.setLevel(logging.INFO)
fh_info.setFormatter(formatter)
logger.addHandler(fh_info)

file_path = os.path.join(log_path, f'debug-{datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.log')
file = open(file_path, 'w')
file.close()

fh_debug = logging.FileHandler(file_path)
fh_debug.setLevel(logging.DEBUG)
fh_debug.setFormatter(formatter)
logger.addHandler(fh_debug)

if __name__ == '__main__':
    logger.info('info')
    logger.debug('debug')
    logger.error('error')
    logger.warning('warning')
    logger.critical('critical')
