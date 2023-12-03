from multiprocessing import Process
from time import time

import cv2
from mediapipe import Image, ImageFormat
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import GestureRecognizerOptions, RunningMode, GestureRecognizer

from src.config import Observer, ConfigCenter

model_asset_path = 'resources/gesture_recognizer.task'

# TODO: 探测区域
options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path),
    running_mode=RunningMode.VIDEO,
    num_hands=1,  # 单手
)


def vision_task(conn, cam=0, flip_y=True):
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
        cap.release()


class VisionTask(Observer):
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
        self.stop()
        self.cam = cam
        self.start()

    def set_flip(self, flip_y):
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
