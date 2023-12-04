from math import sqrt

from cv2 import VideoCapture
from mediapipe.tasks.python.components.containers import NormalizedLandmark

SMOOTHENING = 5  # 平滑系数


class Smoothen:
    """ 平滑算法 """

    def __init__(self, smoothening=SMOOTHENING):
        self.smoothening = smoothening
        self._value = 0

    def getter(self):
        return self._value

    def setter(self, value):
        self._value = self._value + (value - self._value) / self.smoothening

    value = property(getter, setter)


def distance(lm1: NormalizedLandmark, lm2: NormalizedLandmark):
    """两点距离"""
    return sqrt(
        (lm1.x - lm2.x) ** 2
        + (lm1.y - lm2.y) ** 2
        + (lm1.z - lm2.z) ** 2
    )


def zoom(std_dis):
    """TODO: 动态缩放系数
    通过传入标准长度确定缩放系数
    :param std_dis: 标准长度
    """
    # std = std_dis * 10
    # return [1 - std, std]
    return [0.2, 0.8]


def enumerate_devices():
    """获取所有摄像头"""
    device_list = []
    index = 0
    while True:
        cap = VideoCapture(index)
        if cap.isOpened():
            device_list.append(index)
            cap.release()
            index += 1
        else:
            break
    return {f'Camera_{i}': i for i in device_list}
