from time import time

from settings import DEBOUNCE_DELAY_S, SMOOTHENING


class Debounce:
    """防抖算法"""

    def __init__(self, value=None):
        self._value = value
        self.last_change = None

    def getter(self):
        return self._value

    def setter(self, value):
        if self.last_change is None or time() - self.last_change >= DEBOUNCE_DELAY_S:
            self.last_change = time()
            self._value = value

    value = property(getter, setter)


class Smoothen:
    """ 平滑算法 """

    def __init__(self, value=0):
        self._value = value

    def getter(self):
        return self._value

    def setter(self, value):
        self._value = self._value + (value - self._value) / SMOOTHENING

    value = property(getter, setter)
