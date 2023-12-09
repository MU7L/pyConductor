SMOOTHENING = 5  # 平滑系数


class Smoothen:
    """ 平滑算法 """

    def __init__(self, value=0, smoothening=SMOOTHENING):
        self.smoothening = smoothening
        self._value = value

    def getter(self):
        return self._value

    def setter(self, value):
        self._value = self._value + (value - self._value) / self.smoothening

    value = property(getter, setter)
