from PySide6.QtGui import QIcon, QAction, QActionGroup
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from cv2 import VideoCapture

from GUI.app import MyApplication
from utils.config import ConfigCenter, Observer

ICON_PATH = 'resources/icon.png'


# 设备字典


class MyTray(QSystemTrayIcon):
    """托盘"""

    def __init__(self, app: MyApplication, config: ConfigCenter):
        super().__init__()
        self.setIcon(QIcon(ICON_PATH))
        self.setToolTip('pyConductor')
        self.setContextMenu(MyMenu(app, config))


# TODO: 继承改组合
class MyMenu(QMenu):
    """托盘右键菜单"""

    def __init__(self, app: MyApplication, config: ConfigCenter):
        super().__init__()
        self.app = app
        self.observer = MyMenuObserver(self, config)

        # 开始暂停
        label = '开始' if config.get('pause') else '暂停'
        self.start_pause_action = QAction(label, self)

        # 选择设备
        self.device_dict = enumerate_devices()
        self.device_action_group = QActionGroup(self)
        for name, index in self.device_dict.items():
            device_action = QAction(name, self.device_action_group)
            device_action.setCheckable(True)
            if index == config.get('cam'):
                device_action.setChecked(True)
            self.device_action_group.addAction(device_action)

        # 镜像翻转
        self.flip_action = QAction('镜像翻转', self)
        self.flip_action.setCheckable(True)
        self.flip_action.setChecked(config.get('flip'))

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
        """继续暂停"""
        is_running = self.observer.config.get('pause')
        self.observer.config.set('pause', not is_running)

    def handle_device_action(self):
        """选择设备"""
        for action in self.device_action_group.actions():
            if action.isChecked():
                name = action.text()
                self.observer.config.set('cam', self.device_dict[name])
                break

    def handle_flip_action(self):
        """镜像翻转"""
        is_flipped = self.observer.config.get('flip')
        self.observer.config.set('flip', not is_flipped)

    def handle_quit_action(self):
        """退出"""
        self.app.quit()


class MyMenuObserver(Observer):
    """托盘右键菜单观察者"""

    def __init__(self, menu: MyMenu, config: ConfigCenter):
        super().__init__(config)
        self.menu = menu

    def update(self, key, value):
        match key:
            case 'pause':
                self.menu.start_pause_action.setText('开始' if value else '暂停')
            case 'cam':
                for action in self.menu.device_action_group.actions():
                    if action.text() == self.menu.device_dict.get(value):
                        action.setChecked(True)
            case 'flip':
                self.menu.flip_action.setChecked(value)


def enumerate_devices():
    """获取所有摄像头"""
    device_list = []
    index = 0
    while True:
        cap = VideoCapture(index)
        if cap.isOpened():
            device_list.append(index)
            cap.release()
            index += 1
        else:
            break
    return {f'Camera_{i}': i for i in device_list}
