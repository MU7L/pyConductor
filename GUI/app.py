from PySide6.QtWidgets import QApplication

from GUI.tray import MyTray
from GUI.window import MyWindow
from utils.config import ConfigCenter, Observer


class MyApplication(QApplication):

    def __init__(self, config: ConfigCenter):
        super().__init__([])
        MyApplicationObserver(self, config)
        self.tray = MyTray(self, config)
        self.window = MyWindow()

    def start(self):
        """GUI界面启动"""
        self.tray.show()
        self.window.show()
        return self.exec()  # 阻塞

    def stop(self):
        """GUI界面结束"""
        self.tray.hide()
        self.window.hide()
        self.quit()


class MyApplicationObserver(Observer):

    def __init__(self, app: MyApplication, config: ConfigCenter):
        super().__init__(config)
        self.app = app

    def update(self, key, value):
        if key == 'pause':
            if value:
                self.app.window.hide()
            else:
                self.app.window.show()
