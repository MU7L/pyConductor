from typing import Optional

import cv2

from core.job import Job
from utils.config import ConfigCenter
from utils.log import logger


class Collector(Job):
    """收集视频数据任务"""

    def __init__(self, config: ConfigCenter):
        super().__init__(config)
        self.cap: Optional[cv2.VideoCapture] = None
        self.cam: int = self.config.get('cam') or 0
        self.flip_y: bool = self.config.get('flip') or True

    def start(self):
        if self.cap is not None:
            logger.warning('Camera %d is already opened', self.cam)
        else:
            self.cap = cv2.VideoCapture(self.cam)
            self.is_running = True
            logger.info('Opening camera %d', self.cam)

    def read(self):
        try:
            while self.cap.isOpened():
                success, frame = self.cap.read()
                if not success:
                    raise Exception('Cannot read frame')
                self.process(frame)
        except Exception as e:
            logger.exception(e)
        finally:
            self.stop()

    def process(self, frame: cv2.typing.MatLike):
        if self.flip_y:
            frame = cv2.flip(frame, 1)
        self.write(frame=frame)

    def stop(self):
        self.is_running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        logger.info('Camera %d is closed', self.cam)

    def update(self, key, value):
        if key == 'cam' and value != self.cam:
            self.stop()
            self.cam = value
            self.start()
        elif key == 'flip':
            self.flip_y = value
