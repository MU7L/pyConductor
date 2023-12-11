from math import sqrt

from mediapipe.tasks.python.components.containers import NormalizedLandmark
from mediapipe.tasks.python.vision import GestureRecognizerResult
from numpy import interp

from analyzer.core import Gesture, Report
from analyzer.debounce import Debounce
from analyzer.smoothen import Smoothen


class Analyzer:
    """ 将识别结果GestureRecognizerResult解析为Report """

    def __init__(self):
        self.gesture = Debounce('none')
        self.x = Smoothen(0)
        self.y = Smoothen(0)

    def handle(self, result: GestureRecognizerResult):
        if len(result.gestures) == 0:
            return Report(Gesture.NONE, 0, 0)  # 没有检测到手

        gesture_map = {
            'none': Gesture.ELSE,
            'palm': Gesture.PALM,
            'ok': Gesture.OK,
            'fist': Gesture.FIST,
        }
        self.gesture.value = result.gestures[0][0].category_name
        _gesture = gesture_map.get(self.gesture.value) or Gesture.ELSE

        landmarks = result.hand_landmarks[0]
        cursor = landmarks[5]
        # TODO: 标准距离，目前定义为手腕到大拇指根关节距离
        distance_std = distance(landmarks[0], landmarks[1])

        xp = zoom(distance_std)
        self.x.value, self.y.value = interp([cursor.x, cursor.y], xp, [0, 1])

        return Report(_gesture, self.x.value, self.y.value)


def distance(lm1: NormalizedLandmark, lm2: NormalizedLandmark):
    """两点距离"""
    return sqrt(
        (lm1.x - lm2.x) ** 2
        + (lm1.y - lm2.y) ** 2
        + (lm1.z - lm2.z) ** 2
    )


def zoom(std_dis):
    """TODO: 动态缩放系数 通过传入标准长度确定缩放系数
    :param std_dis: 标准长度
    """
    std = std_dis * 10
    # return [1 - std, std]
    return [0.2, 0.8]
