from enum import Enum

from PySide6.QtCore import Qt, QTimer, QTimeLine
from PySide6.QtGui import QPainter, QGuiApplication, QColor, QRegion, QIcon, QPixmap
from PySide6.QtWidgets import QWidget, QApplication

from analyzer.core import Gesture
from utils.config import Observer, ConfigCenter

FPS = 60  # 刷新率
R = 30  # 半径
RING_WIDTH = 5  # 色环宽度

ICON_PATH_MAP = {
    'eye': 'resources/png/eye.png',
    'palm': 'resources/png/palm.png',
    'ok': 'resources/png/ok.png',
    'fist': 'resources/png/fist.png',
}


class RingStyle(Enum):
    """指示环样式"""
    DEFAULT = 0
    BLUE = 1
    GREEN = 2
    RED = 3
    JUDGING = 4


class MyWindow(QWidget):
    """主界面"""

    def __init__(self, config: ConfigCenter):
        super().__init__()
        self.observer = MyWindowObserver(self, config)

        self.init_ui()

        self.pix_map = {
            Gesture.NONE: QPixmap(ICON_PATH_MAP['eye']),
            Gesture.PALM: QPixmap(ICON_PATH_MAP['palm']),
            Gesture.OK: QPixmap(ICON_PATH_MAP['ok']),
            Gesture.FIST: QPixmap(ICON_PATH_MAP['fist']),
            Gesture.ELSE: QPixmap(ICON_PATH_MAP['palm']),
        }
        self.current_gesture = Gesture.NONE
        self.setWindowIcon(self.pix_map[self.current_gesture])

        screen = QGuiApplication.primaryScreen().geometry()
        self.screen_width = screen.width()
        self.screen_height = screen.height()

        self.cursor_x = self.screen_width / 2
        self.cursor_y = self.screen_height / 2
        self.ring_deg = 360
        self.ring_front_color = QColor(Qt.transparent)
        self.ring_back_color = QColor(Qt.transparent)

        self.ring_timeline = QTimeLine(1000, self)
        self.ring_timeline.setFrameRange(0, 360)
        self.ring_timeline.frameChanged.connect(self.on_frame_changed)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)

        self.is_show = False
        self.setWindowOpacity(0)
        # self.timer.start(int(1000 / FPS))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        bg, ring, cursor = self.divide_region()

        # 背景
        painter.setClipRegion(bg)
        painter.fillRect(bg.boundingRect(), QColor(0, 0, 0, 127))
        # 环
        painter.setClipRegion(ring)
        painter.setBrush(self.ring_back_color)
        painter.drawPie(ring.boundingRect(), 0, 360 * 16)
        painter.setBrush(self.ring_front_color)
        painter.drawPie(ring.boundingRect(), 0, self.ring_deg * 16)
        # 指示器
        painter.setClipRegion(cursor)
        painter.fillRect(cursor.boundingRect(), QColor(0, 0, 0, 0))

    def show(self):
        if not self.is_show:
            self.is_show = True
            # self.timer.stop()
            self.setWindowOpacity(1)
            # self.timer.start(int(1000 / FPS))

    def hide(self):
        if self.is_show:
            self.is_show = False
            self.ring_timeline.stop()
            # self.timer.stop()
            self.setWindowOpacity(0)

    def init_ui(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint  # 无边框
            | Qt.WindowStaysOnTopHint  # 置顶
            | Qt.WindowTransparentForInput  # 鼠标穿透
            # | Qt.ToolTip  # 无任务栏图标
        )
        self.setAttribute(Qt.WA_TranslucentBackground)  # 透明

    def on_frame_changed(self, frame):
        self.ring_deg = frame
        self.update()

    def divide_region(self):
        cursor = QRegion(self.cursor_x - R, self.cursor_y - R, R * 2, R * 2, QRegion.Ellipse)
        tmp = QRegion(self.cursor_x - R - RING_WIDTH, self.cursor_y - R - RING_WIDTH, (R + RING_WIDTH) * 2,
                      (R + RING_WIDTH) * 2, QRegion.Ellipse)
        ring = tmp.subtracted(cursor)
        bg = self.visibleRegion().subtracted(tmp)
        return bg, ring, cursor

    def move_to(self, x, y):
        self.cursor_x, self.cursor_y = x * self.screen_width, y * self.screen_height
        self.update()

    def set_ring(self, style: RingStyle = None, duration: int = 1000):
        self.ring_timeline.stop()
        match style:
            case RingStyle.BLUE:
                self.ring_deg = 360
                self.ring_front_color = QColor(Qt.blue)
                self.ring_back_color = QColor(Qt.blue)
            case RingStyle.GREEN:
                self.ring_deg = 360
                self.ring_front_color = QColor(Qt.green)
                self.ring_back_color = QColor(Qt.green)
            case RingStyle.RED:
                self.ring_deg = 360
                self.ring_front_color = QColor(Qt.red)
                self.ring_back_color = QColor(Qt.red)
            case RingStyle.JUDGING:
                self.ring_deg = 0
                self.ring_front_color = QColor(Qt.red)
                self.ring_back_color = QColor(Qt.blue)
                self.ring_timeline.setDuration(duration)
                self.ring_timeline.start()
            case _:
                self.ring_deg = 360
                self.ring_front_color = QColor(Qt.transparent)
                self.ring_back_color = QColor(Qt.transparent)
        self.update()

    def set_icon(self, gesture: Gesture):
        if gesture is not self.current_gesture:
            self.current_gesture = gesture
            self.setWindowIcon(self.pix_map[self.current_gesture])
            print(self.pix_map[self.current_gesture])


class MyWindowObserver(Observer):

    def __init__(self, window: MyWindow, config: ConfigCenter):
        super().__init__(config)
        self.window = window

    def update(self, key, value):
        if key == 'pause':
            if value:
                self.window.hide()
            else:
                self.window.show()
