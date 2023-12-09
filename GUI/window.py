from enum import Enum

from PySide6.QtCore import Qt, QTimer, QTimeLine
from PySide6.QtGui import QPainter, QGuiApplication, QColor, QRegion
from PySide6.QtWidgets import QWidget

FPS = 60  # 刷新率
R = 30  # 半径
RING_WIDTH = 5  # 色环宽度


class RingStyle(Enum):
    """指示环样式"""
    DEFAULT = 0
    BLUE = 1
    GREEN = 2
    RED = 3
    JUDGING = 4


class MyWindow(QWidget):
    """主界面"""

    def __init__(self):
        super().__init__()

        self.init_ui()

        screen = QGuiApplication.primaryScreen().geometry()
        self.screen_width = screen.width()
        self.screen_height = screen.height()

        self.is_show = False
        self.x = self.screen_width / 2
        self.y = self.screen_height / 2
        self.ring_deg = 360
        self.ring_front_color = QColor(Qt.transparent)
        self.ring_back_color = QColor(Qt.transparent)

        self.ring_timeline = QTimeLine(1000, self)
        self.ring_timeline.setFrameRange(0, 360)
        self.ring_timeline.frameChanged.connect(self.ring_deg_increase)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)
        bg, ring, cursor = self.divide_region()

        # 背景
        painter.setClipRegion(bg)
        painter.fillRect(bg.boundingRect(), QColor(0, 0, 0, 127))
        # 环
        painter.setClipRegion(ring)
        painter.setBrush(self.ring_front_color)
        painter.drawPie(ring.boundingRect(), 0, self.ring_deg * 16)
        painter.setBrush(self.ring_back_color)
        painter.drawPie(ring.boundingRect(), self.ring_deg * 16, 360 * 16)
        # 指示器
        painter.setClipRegion(cursor)
        painter.fillRect(cursor.boundingRect(), QColor(0, 0, 0, 0))

    def show(self):
        if not self.is_show:
            self.is_show = True
            self.timer.start(int(1000 / FPS))
            self.showFullScreen()

    def hide(self):
        if self.is_show:
            self.is_show = False
            self.ring_timeline.stop()
            self.timer.stop()
            super().hide()

    def init_ui(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint  # 无边框
            | Qt.WindowStaysOnTopHint  # 置顶
            | Qt.WindowTransparentForInput  # 鼠标穿透
            | Qt.ToolTip  # 无任务栏图标
        )
        self.setAttribute(Qt.WA_TranslucentBackground)  # 透明

    def ring_deg_increase(self):
        self.ring_deg += 1

    def divide_region(self):
        cursor = QRegion(self.x - R, self.y - R, R * 2, R * 2, QRegion.Ellipse)
        tmp = QRegion(self.x - R - RING_WIDTH, self.y - R - RING_WIDTH, (R + RING_WIDTH) * 2, (R + RING_WIDTH) * 2,
                      QRegion.Ellipse)
        ring = tmp.subtracted(cursor)
        bg = self.visibleRegion().subtracted(tmp)
        return bg, ring, cursor

    def move_to(self, x, y):
        self.x = x * self.screen_width
        self.y = y * self.screen_height

    def set_ring(self, style: RingStyle = None):
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
                self.ring_timeline.start()
            case _:
                self.ring_deg = 360
                self.ring_front_color = QColor(Qt.transparent)
                self.ring_back_color = QColor(Qt.transparent)
