from PySide6.QtGui import QAction, QActionGroup, QPixmap
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from cv2 import VideoCapture

from settings import ICON_PATH
from utils.config import ConfigCenter, Observer
from utils.log import logger


class MyTray(QSystemTrayIcon):
    """托盘"""

    def __init__(self, app: QApplication, config: ConfigCenter):
        pixmap = QPixmap(ICON_PATH)
        super().__init__(pixmap, app)
        self.setToolTip('pyConductor')
        self.setContextMenu(MyMenu(app, self, config))

        self.activated.connect(self.on_activated)

    def on_activated(self, reason):
        # TODO: 处理托盘的点击事件
        pass


class MyMenu(QMenu):
    """托盘右键菜单"""

    def __init__(self, app: QApplication, tray: MyTray, config: ConfigCenter):
        super().__init__()
        self.app = app
        self.tray = tray
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

    def handle_device_action(self, action):
        """选择设备"""
        name = action.text()
        self.observer.config.set('cam', self.device_dict[name])

    def handle_flip_action(self):
        """镜像翻转"""
        is_flipped = self.observer.config.get('flip')
        self.observer.config.set('flip', not is_flipped)

    def handle_quit_action(self):
        """退出"""
        self.tray.hide()
        self.app.quit()


class MyMenuObserver(Observer):
    """托盘右键菜单观察者"""

    # TODO: 是否需要绑定信号槽？
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
    devices = []
    index = 0
    while True:
        cap = VideoCapture(index)
        if cap.isOpened():
            devices.append(index)
            cap.release()
            index += 1
        else:
            break
    res = {f'Camera_{i}': i for i in devices}
    logger.info(f'Cameras: {res}')
    return res
