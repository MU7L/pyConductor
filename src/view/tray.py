from PySide6.QtGui import QIcon, QAction, QActionGroup
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication

from src.config import ConfigCenter
from src.utils import enumerate_devices

icon_path = 'resources/icon.png'

device_dict = enumerate_devices()


class MyMenu(QMenu):
    def __init__(self, tray: QSystemTrayIcon, config: ConfigCenter):
        super().__init__()
        self.tray = tray
        self.config = config

        # 开始暂停
        self.start_pause_action = QAction('暂停', self)

        # 选择设备
        self.device_action_group = QActionGroup(self)
        for name, index in device_dict.items():
            device_action = QAction(name, self.device_action_group)
            device_action.setCheckable(True)
            if index == self.config.get('cam'):
                device_action.setChecked(True)
            self.device_action_group.addAction(device_action)

        # 镜像翻转
        self.flip_action = QAction('镜像翻转', self)
        self.flip_action.setCheckable(True)
        self.flip_action.setChecked(self.config.get('flip'))

        # 退出
        self.quit_action = QAction('退出', self)

        self.init_ui()
        self.init_connect()

    def init_ui(self):
        self.addAction(self.start_pause_action)
        self.addSeparator()
        self.addActions(self.device_action_group.actions())
        self.addSeparator()
        self.addAction(self.flip_action)
        self.addSeparator()
        self.addAction(self.quit_action)

    def init_connect(self):
        self.start_pause_action.triggered.connect(self.handle_start_pause_action)
        self.device_action_group.triggered.connect(self.handle_device_action)
        self.flip_action.triggered.connect(self.handle_flip_action)
        self.quit_action.triggered.connect(self.handle_quit_action)

    def handle_start_pause_action(self):
        is_running = self.config.get('run')
        self.config.set('run', not is_running)
        self.start_pause_action.setText('暂停' if is_running else '开始')

    def handle_device_action(self):
        for action in self.device_action_group.actions():
            if action.isChecked():
                name = action.text()
                self.config.set('cam', device_dict[name])
                break

    def handle_flip_action(self):
        is_flipped = self.config.get('flip')
        self.config.set('flip', not is_flipped)
        self.flip_action.setChecked(not is_flipped)

    def handle_quit_action(self):
        self.tray.hide()
        self.config.set('run', False)
        QApplication.instance().quit()


class MyTray(QSystemTrayIcon):
    def __init__(self, config: ConfigCenter):
        super().__init__()
        self.setIcon(QIcon(icon_path))
        self.setToolTip('pyConductor')
        self.setContextMenu(MyMenu(self, config))
