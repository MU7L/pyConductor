from math import sqrt

from cv2 import VideoCapture
from mediapipe.tasks.python.components.containers import NormalizedLandmark
from mediapipe.tasks.python.vision import GestureRecognizerResult

from src.core import Report, Signal

settings = {
    'pinch_threshold': 0.5,
    'smoothening': 5
}


class Smoothen:
    def __init__(self, smoothening=settings['smoothening']):
        self.smoothening = smoothening
        self._value = 0

    def getter(self):
        return self._value

    def setter(self, value):
        self._value = self._value + (value - self._value) / self.smoothening

    value = property(getter, setter)


class ResultParser:
    def __init__(self):
        self.x = Smoothen()
        self.y = Smoothen()

    def handle(self, result: GestureRecognizerResult):
        if len(result.gestures) == 0:
            return Report(Signal.NONE, 0, 0)

        gesture = result.gestures[0][0]
        landmarks = result.hand_landmarks[0]
        cursor = landmarks[5]
        self.x.value = cursor.x
        self.y.value = cursor.y

        if gesture.category_name == 'Closed_Fist':
            return Report(Signal.GRAB, self.x.value, self.y.value)

        distance_std = distance(landmarks[0], landmarks[1])
        distance_04_08 = distance(landmarks[4], landmarks[8])
        distance_04_12 = distance(landmarks[4], landmarks[12])
        # print(distance_04_08 / distance_std)

        if distance_04_08 / distance_std <= settings['pinch_threshold']:
            return Report(Signal.LEFT, self.x.value, self.y.value)

        if distance_04_12 / distance_std <= settings['pinch_threshold']:
            return Report(Signal.RIGHT, self.x.value, self.y.value)

        return Report(Signal.ONE, self.x.value, self.y.value)


def distance(lm1: NormalizedLandmark, lm2: NormalizedLandmark):
    return sqrt(
        (lm1.x - lm2.x) ** 2
        + (lm1.y - lm2.y) ** 2
        + (lm1.z - lm2.z) ** 2
    )


def enumerate_devices():
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
