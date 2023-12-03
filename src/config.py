default_data = {
    'run': True,
    'cam': 0,
    'flip': True
}


class ConfigCenter:
    def __init__(self, data_dict=None):
        if data_dict is None:
            data_dict = default_data
        self.data = data_dict
        self.observers: list[Observer] = []

    def register(self, observer):
        if observer not in self.observers:
            self.observers.append(observer)

    def set(self, key, value):
        self.data[key] = value
        for observer in self.observers:
            observer.update(key, value)

    def get(self, key):
        return self.data.get(key)


class Observer:
    def __init__(self, config: ConfigCenter):
        self.config = config
        config.register(self)

    def update(self, key, value):
        pass
