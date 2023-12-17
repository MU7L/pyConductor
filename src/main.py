from PySide6.QtWidgets import QApplication

from thread.signals import Signals
from thread.worker import Worker
from utils.config import ConfigCenter
from views.tray import MyTray
from views.window import MyWindow


def main():
    config = ConfigCenter()

    app = QApplication([])
    signals = Signals()
    worker = Worker(app, signals, config)
    tray = MyTray(app, config)
    window = MyWindow(signals, config)

    # 运行
    tray.show()
    window.showFullScreen()
    worker.start()
    app.exec()


if __name__ == '__main__':
    main()
