import sys
from multiprocessing import Pipe
from threading import Event, Thread

from GUI.app import MyApplication
from analyzer.analyzer import Analyzer
from machine.machine import Machine
from recognizer.core import TaskResult
from recognizer.recognizer import Recognizer
from utils.config import ConfigCenter
from utils.logger import logger

default_settings = {
    'run': True,
    'cam': 0,
    'flip': True
}


class App:
    def __init__(self, settings=None):
        # 配置中心
        if settings is None:
            settings = default_settings
        self.config = ConfigCenter(settings)

        # 通信管道
        self.left, self.right = Pipe()

        # 事件处理
        self.event = Event()

        # 识别模块
        self.recognizer = Recognizer(self.left, self.config)

        # 接收模块
        self.recv_thread = Thread(target=self.recv)
        self.recv_thread.daemon = True

        # 显示模块
        self.gui = MyApplication(self.config)

        # 鼠标控制模块
        self.machine = Machine(self.gui.window, self.config)

    def recv(self):
        """接收线程"""
        analyzer = Analyzer()
        while not self.event.is_set():
            if self.config.get('pause'):
                continue
            tr: TaskResult = self.right.recv()
            report = analyzer.handle(tr.result)
            logger.debug(report)
            self.machine.handle(report)

    def start(self):
        self.recognizer.start()
        self.recv_thread.start()
        return self.gui.start()  # 阻塞

    def stop(self):
        self.config.set('pause', True)
        self.event.set()
        self.left.close()
        self.right.close()
        self.recognizer.stop()
        self.gui.stop()

    def exec(self):
        code = self.start()  # 阻塞
        self.stop()
        return code


def main():
    app = App()
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
