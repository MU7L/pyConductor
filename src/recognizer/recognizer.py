from multiprocessing import Process, Pipe
from time import time

from recognizer.vision_task import vision_task
from utils.config import Observer, ConfigCenter
from utils.log import logger


# TODO: 用共享内存实现多进程通信
class Recognizer(Observer):
    """手势识别任务代理类"""

    def __init__(self, config: ConfigCenter):
        super().__init__(config)
        self.input, self.output = Pipe()
        self.cam = self.config.get('cam') or 0
        self.flip_y = self.config.get('flip') or False
        self.start_time = None
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
        self.terminate(False)
        self.cam = cam
        self.start()

    def set_flip(self, flip_y):
        if self.flip_y == flip_y:
            return
        self.terminate(False)
        self.flip_y = flip_y
        self.start()

    def start(self):
        if self.process is None:
            self.process = Process(name='Task_Vision', target=vision_task, args=(self.input, self.cam, self.flip_y))
            self.process.daemon = True
            self.process.start()
            self.start_time = time()
        logger.info(f'Recognizer started. cam: {self.cam}, flip: {self.flip_y}.')

    def terminate(self, close_pipe=True):
        if self.process is not None:
            self.process.terminate()
            self.process.join()
            self.process = None
        if close_pipe:
            self.input.close()
            self.output.close()
        logger.info(f'Recognizer stopped. running {time() - self.start_time} seconds.')
        self.start_time = None
