from PySide6.QtWidgets import QApplication

from machine.machine import Machine
from utils.config import ConfigCenter
from views.tray import MyTray
from views.window import MyWindow


def main():
    config = ConfigCenter()
    app = QApplication([])
    machine = Machine(app, config)
    tray = MyTray(app, config)
    window = MyWindow(machine, config)

    # 运行
    tray.show()
    window.showFullScreen()
    machine.start()
    app.exec()


if __name__ == '__main__':
    main()
