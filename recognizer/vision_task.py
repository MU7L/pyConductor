from time import time

from cv2 import VideoCapture, flip
from mediapipe import Image, ImageFormat
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import GestureRecognizerOptions, RunningMode, GestureRecognizer

from recognizer.core import TaskResult
from utils.logger import logger

MODEL_ASSET_PATH = 'resources/gesture_recognizer.task'

options = GestureRecognizerOptions(
    base_options=BaseOptions(MODEL_ASSET_PATH),
    running_mode=RunningMode.VIDEO,
    num_hands=1,  # 单手
)


def vision_task(conn, cam=0, flip_y=True):
    """手势识别任务"""
    with GestureRecognizer.create_from_options(options) as recognizer:
        cap = VideoCapture(cam)
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                print('Failed to capture image')
                continue
            frame_timestamp_ms = int(time() * 1000)
            if flip_y:
                frame = flip(frame, 1)
            mp_image = Image(image_format=ImageFormat.SRGB, data=frame)
            result = recognizer.recognize_for_video(mp_image, frame_timestamp_ms)
            # logger.debug(result.gestures)
            task_result = TaskResult(frame, result)
            conn.send(task_result)
        cap.release()
