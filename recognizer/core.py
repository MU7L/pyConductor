from cv2 import Mat
from mediapipe.tasks.python.vision import GestureRecognizerResult
from numpy import ndarray, dtype, generic

Frame = Mat | ndarray[any, dtype[generic]] | ndarray


class TaskResult:
    """vision task 产出的数据，包含检测图像和识别结果"""

    def __init__(self, frame: Frame, result: GestureRecognizerResult):
        self.frame = frame
        self.result = result

    def __repr__(self):
        frame_repr = "frame" if self.frame is not None else "no frame"
        result_repr = f"{len(self.result.gestures)} results"
        return f"TaskResult({frame_repr}, {result_repr})"
