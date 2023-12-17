import math

import numpy as np
from mediapipe.tasks.python.components.containers import NormalizedLandmark
from mediapipe.tasks.python.vision import GestureRecognizerResult

from core.data import Gesture, Report
from core.job import Job
from utils.algorithms import Debounce, Smoothen
from utils.config import ConfigCenter
from utils.log import logger


class Analyzer(Job):
    """ 将识别结果GestureRecognizerResult解析为Report """

    def __init__(self, config: ConfigCenter):
        super().__init__(config)
        self.gesture = Debounce('none')
        self.x = Smoothen(0)
        self.y = Smoothen(0)
        self.xp = [0.2, 0.8]

    def adapt(self, std_dis: float):
        """TODO: 根据标准长自适应调整部分参数
        :param std_dis: 标准距离。值越小，表明手距离摄像头越远
        """
        # 检测区域：手越远，检测区域越小
        tmp = max(min((0.032 / std_dis), 0.5), 0)
        self.xp = [tmp, 1 - tmp]
        # 防抖系数：手越远，防抖系数越大
        # tmp = 0.1 / std_dis
        # self.x.adaptation = tmp
        # self.y.adaptation = tmp

    def process(self, result: GestureRecognizerResult):
        if len(result.gestures) == 0:
            self.write(Report(Gesture.NONE, 0, 0))  # 没有检测到手
            return

        # 手势
        gesture_map = {
            'palm': Gesture.PALM,
            'ok':   Gesture.OK,
            'fist': Gesture.FIST,
        }
        self.gesture.value = result.gestures[0][0].category_name
        _gesture = gesture_map.get(self.gesture.value) or Gesture.ELSE

        landmarks = result.hand_landmarks[0]
        # TODO: 标准距离，目前定义为手腕到大拇指根关节距离
        distance_std = distance(landmarks[0], landmarks[1])
        self.adapt(distance_std)

        # 指针位置
        cursor = landmarks[5]
        self.x.value, self.y.value = np.interp([cursor.x, cursor.y], self.xp, [0, 1])

        self.write(Report(_gesture, self.x.value, self.y.value))


def distance(lm1: NormalizedLandmark, lm2: NormalizedLandmark) -> float:
    """两点距离"""
    return math.sqrt(
        (lm1.x - lm2.x) ** 2
        + (lm1.y - lm2.y) ** 2
        + (lm1.z - lm2.z) ** 2
    )
