import sys
from multiprocessing import Pipe
from threading import Event, Thread

from PySide6.QtWidgets import QApplication

from src.config import ConfigCenter
from src.controller import Machine
from src.utils import ResultParser
from src.view.tray import MyTray
from src.view.window import MyWindow
from src.vision_task import VisionTask

default_settings = {
    'run': True,
    'cam': 1,
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
        self.task = VisionTask(self.left, self.config)
        # 接收模块
        self.recv_thread = Thread(target=self.recv)
        self.recv_thread.daemon = True
        # 鼠标控制模块
        self.machine = Machine()
        # 显示模块
        self.app = QApplication()
        self.window = MyWindow()
        # 系统控制模块
        self.tray = MyTray(self.config)

    def recv(self):
        # 接收线程
        result_parser = ResultParser()
        while not self.event.is_set():
            if not self.config.get('run'):
                continue
            result = self.right.recv()
            report = result_parser.handle(result)
            print(report)
            self.machine.handle(report)
            self.window.handle(report)

    def start(self):
        self.task.start()
        self.window.showFullScreen()
        self.tray.show()
        self.recv_thread.start()
        return self.app.exec()  # 阻塞

    def stop(self):
        self.config.set('run', False)
        self.event.set()
        self.left.close()
        self.right.close()
        self.task.stop()
        self.tray.hide()
        self.window.close()


def main():
    app = Application()
    code = app.start()
    app.stop()
    return code


if __name__ == '__main__':
    sys.exit(main())
