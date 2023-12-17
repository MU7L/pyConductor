from settings import base_config
from utils.log import logger


class ConfigCenter:
    """配置中心，实现观察者模式"""

    def __init__(self):
        self.config = base_config
        self.observers: list[Observer] = []
        logger.info('initialize config center: %s', str(self.config))

    def register(self, observer):
        if observer not in self.observers:
            self.observers.append(observer)

    def set(self, key, value):
        try:
            if key not in self.config:
                raise KeyError(f'key {key} not in config')
            self.config[key] = value
            logger.info('set config %s to %s', key, str(value))
            for observer in self.observers:
                observer.update(key, value)
        except KeyError as e:
            logger.exception(e)

    def get(self, key):
        return self.config.get(key)


class Observer:
    """观察者"""

    def __init__(self, config: ConfigCenter):
        self.config = config
        config.register(self)

    def update(self, key, value):
        pass
