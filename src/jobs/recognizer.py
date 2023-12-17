import multiprocessing
import threading
import time
from typing import Optional

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from core.job import Job
from settings import TASK_PATH
from utils.config import ConfigCenter
from utils.log import logger

options = vision.GestureRecognizerOptions(
    base_options=python.BaseOptions(TASK_PATH),
    running_mode=vision.RunningMode.VIDEO,
    num_hands=1,  # 单手
)


def vision_task(conn):
    """手势识别任务"""
    # TODO: 是否有优化空间
    with vision.GestureRecognizer.create_from_options(options) as recognizer:
        while True:
            frame = conn.recv()
            frame_timestamp_ms = int(time.time() * 1000)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
            result = recognizer.recognize_for_video(mp_image, frame_timestamp_ms)
            conn.send(result)


class Recognizer(Job):
    """手势识别任务"""

    def __init__(self, config: ConfigCenter):
        super().__init__(config)
        self.main_conn, self.sub_conn = multiprocessing.Pipe()
        threading.Thread(target=self.process, daemon=True).start()
        self.p: Optional[multiprocessing.Process] = None

    def start(self):
        if self.p is None:
            self.p = multiprocessing.Process(name='Task_Vision', target=vision_task, args=(self.sub_conn,))
            self.p.daemon = True
            self.p.start()
            logger.info('Recognizer started.')
        else:
            logger.warning('Recognizer already started.')
        self.is_running = True

    def read(self, frame: cv2.typing.MatLike):
        self.main_conn.send(frame)

    def process(self):
        while True:
            result = self.main_conn.recv()
            self.write(result=result)

    def stop(self, close_pipe=True):
        self.is_running = False
        if self.p is not None:
            self.p.terminate()
            self.p.join()
            self.p = None
            logger.info('Recognizer stopped.')
        else:
            logger.warning('Recognizer already stopped.')
        if close_pipe:
            self.main_conn.close()
            self.sub_conn.close()
            logger.info('Recognizer pipe closed.')
