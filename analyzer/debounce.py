from time import time

DEBOUNCE_DELAY = 0.07  # 防抖延时


class Debounce:
    """防抖算法"""

    def __init__(self, value=None, delay=DEBOUNCE_DELAY):
        self.delay = delay
        self._value = value
        self.last_change = None

    def getter(self):
        return self._value

    def setter(self, value):
        if self.last_change is None or time() - self.last_change >= self.delay:
            self.last_change = time()
            self._value = value

    value = property(getter, setter)
