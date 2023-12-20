from PySide6.QtWidgets import QApplication


from utils.config import ConfigCenter
from views.tray import MyTray
from views.window import MyWindow
from worker.signals import Signals
from worker.worker import Worker


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
