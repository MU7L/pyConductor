class ConfigCenter:
    """配置中心，实现观察者模式"""

    def __init__(self, data_dict=None):
        if data_dict is None:
            data_dict = {
                'pause': False,  # 暂停
                'cam': 0,  # 相机编号
                'flip': True,  # 镜像
            }
        self.data = data_dict
        self.observers: list[Observer] = []

    def register(self, observer):
        if observer not in self.observers:
            self.observers.append(observer)

    def set(self, key, value):
        if key not in self.data:
            raise KeyError(f'key {key} not in config')
        self.data[key] = value
        for observer in self.observers:
            observer.update(key, value)

    def get(self, key):
        return self.data.get(key)


class Observer:
    """观察者"""

    def __init__(self, config: ConfigCenter):
        self.config = config
        config.register(self)

    def update(self, key, value):
        pass
