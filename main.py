import sys
from multiprocessing import Pipe
from threading import Event, Thread

from PySide6.QtWidgets import QApplication

from GUI.tray import MyTray
from GUI.window import MyWindow
from GUI.window2 import MyWidget
from analyzer.analyzer import Analyzer
from machine.machine import Machine
from recognizer.core import TaskResult
from recognizer.recognizer import Recognizer
from utils.config import ConfigCenter
from utils.logger import logger

default_settings = {
    'pause': False,
    'cam': 0,
    'flip': True
}


class Application:
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
        self.app = QApplication([])
        self.tray = MyTray(self.config)
        # self.window = MyWindow(self.config)
        self.widget = MyWidget()

        # 系统控制模块
        # self.machine = Machine(self.window, self.config)
        self.machine = Machine(self.widget, self.config)

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
        self.tray.show()
        # self.window.showFullScreen()
        self.widget.show()
        return self.app.exec()  # 阻塞

    def stop(self):
        self.config.set('pause', True)
        self.recognizer.stop()
        self.event.set()
        self.left.close()
        self.right.close()

    def exec(self):
        code = self.start()  # 阻塞
        self.stop()
        return code


def main():
    app = Application()
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
