from multiprocessing import Process

from recognizer.vision_task import vision_task
from utils.config import Observer, ConfigCenter
from utils.logger import logger


class Recognizer(Observer):
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
        logger.info(f'Recognizer started. cam: {self.cam}, flip: {self.flip_y}')

    def stop(self):
        self.process.terminate()
        self.process.join()
        self.process = None
        logger.info('Recognizer stopped')
