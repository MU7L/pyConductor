from mediapipe.tasks.python.vision import GestureRecognizerResult
from numpy import interp

from src.core import Report, Signal
from src.utils import Smoothen, distance, zoom

PINCH_THRESHOLD = 0.5  # 手指合拢阈值


class ResultParser:
    """ 将识别结果GestureRecognizerResult解析为Report """

    def __init__(self, pinch_threshold=PINCH_THRESHOLD):
        self.x = Smoothen()
        self.y = Smoothen()
        self.pinch_threshold = pinch_threshold

    def handle(self, result: GestureRecognizerResult):
        if len(result.gestures) == 0:
            return Report(Signal.NONE, 0, 0)  # 无手势

        gesture = result.gestures[0][0]
        landmarks = result.hand_landmarks[0]
        cursor = landmarks[5]
        distance_std = distance(landmarks[0], landmarks[1])  # TODO: 标准距离，目前定义为手腕到大拇指根关节距离

        xp = zoom(distance_std)
        self.x.value = interp(cursor.x, xp, [0, 1])
        self.y.value = interp(cursor.y, xp, [0, 1])

        if gesture.category_name == 'Closed_Fist':
            return Report(Signal.GRAB, self.x.value, self.y.value)  # 翻页手势

        distance_04_08 = distance(landmarks[4], landmarks[8])
        distance_04_12 = distance(landmarks[4], landmarks[12])
        # print(distance_std)

        if distance_04_08 / distance_std <= self.pinch_threshold:
            return Report(Signal.LEFT, self.x.value, self.y.value)  # 左键手势

        if distance_04_12 / distance_std <= self.pinch_threshold:
            return Report(Signal.RIGHT, self.x.value, self.y.value)  # 右键手势

        return Report(Signal.ONE, self.x.value, self.y.value)  # 移动手势
