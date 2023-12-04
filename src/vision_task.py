from multiprocessing import Process
from time import time

import cv2
from mediapipe import Image, ImageFormat
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import GestureRecognizerOptions, RunningMode, GestureRecognizer

from src.config import Observer, ConfigCenter

MODEL_ASSET_PATH = 'resources/gesture_recognizer.task'

options = GestureRecognizerOptions(
    base_options=BaseOptions(MODEL_ASSET_PATH),
    running_mode=RunningMode.VIDEO,
    num_hands=1,  # 单手
)


def vision_task(conn, cam=0, flip_y=True):
    """手势识别任务"""
    with GestureRecognizer.create_from_options(options) as recognizer:
        cap = cv2.VideoCapture(cam)
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                print('Failed to capture image')
                continue
            frame_timestamp_ms = int(time() * 1000)
            if flip_y:
                frame = cv2.flip(frame, 1)
            mp_image = Image(image_format=ImageFormat.SRGB, data=frame)
            result = recognizer.recognize_for_video(mp_image, frame_timestamp_ms)
            conn.send(result)
            # TODO: 可视化
        cap.release()


class VisionTask(Observer):
    """手势识别任务代理类"""

    def __init__(self, conn, config: ConfigCenter):
        super().__init__(config)
        self.conn = conn
        self.cam = self.config.get('cam') or 0
        self.flip_y = self.config.get('flip') or False
        self.process = None

    def update(self, key, value):
        match key:
            case 'cam':
                self.set_cam(value)
            case 'flip':
                self.set_flip(value)

    def set_cam(self, cam):
        if self.cam == cam:
            return
        self.stop()
        self.cam = cam
        self.start()

    def set_flip(self, flip_y):
        if self.flip_y == flip_y:
            return
        self.stop()
        self.flip_y = flip_y
        self.start()

    def start(self):
        if self.process is None:
            self.process = Process(name='Task_Vision', target=vision_task, args=(self.conn, self.cam, self.flip_y))
            self.process.daemon = True
        self.process.start()
        # toast('原神，启动！')

    def stop(self):
        self.process.terminate()
        self.process.join()
        self.process = None
