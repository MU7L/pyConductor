import os

from PySide6 import QtCore
from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QColor, QGuiApplication, QPainter, QPixmap, QRegion
from PySide6.QtWidgets import QWidget

from core.data import Gesture
from settings import PNG_PATH, RING_D, RING_R

from utils.config import ConfigCenter, Observer
from views.ring_style import RingStyle
from worker.signals import Signals

ICON_PATH_MAP = {
    'eye':  os.path.join(PNG_PATH, 'eye.png'),
    'palm': os.path.join(PNG_PATH, 'palm.png'),
    'ok':   os.path.join(PNG_PATH, 'ok.png'),
    'fist': os.path.join(PNG_PATH, 'fist.png'),
}


class MyWindow(QWidget):
    """主界面"""

    def __init__(self, signals: Signals, config: ConfigCenter):
        super().__init__()
        # 受config center控制
        self.observer = MyWindowObserver(self, config)

        # 初始化UI
        self.init_ui()

        # 屏幕尺寸
        screen = QGuiApplication.primaryScreen().geometry()
        self.screen_width = screen.width()
        self.screen_height = screen.height()

        # 初始化信号槽
        self.init_sig(signals)

        # 显示控制
        self.setWindowOpacity(0)

        # 指示环位置
        self.cursor_x = self.screen_width / 2
        self.cursor_y = self.screen_height / 2

        # 指示环样式
        self.ring_deg = 0
        self.ring_front_color = Qt.transparent
        self.ring_back_color = Qt.transparent
        self.ring_timeline = QtCore.QTimeLine(1000, self)
        self.ring_timeline.setFrameRange(0, 360)
        self.ring_timeline.frameChanged.connect(self.on_frame_changed)

        # 任务栏图标
        self.gesture_pix_map = {
            Gesture.NONE: QPixmap(ICON_PATH_MAP['eye']),
            Gesture.PALM: QPixmap(ICON_PATH_MAP['palm']),
            Gesture.OK:   QPixmap(ICON_PATH_MAP['ok']),
            Gesture.FIST: QPixmap(ICON_PATH_MAP['fist']),
            Gesture.ELSE: QPixmap(ICON_PATH_MAP['palm']),
        }
        self.current_gesture = Gesture.NONE
        self.setWindowIcon(self.gesture_pix_map[self.current_gesture])

    def init_ui(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint  # 无边框
            | Qt.WindowStaysOnTopHint  # 置顶
            | Qt.WindowTransparentForInput  # 鼠标穿透
        )
        self.setAttribute(Qt.WA_TranslucentBackground)  # 透明

    def init_sig(self, signals: Signals):
        signals.show_sig.connect(self.on_show_sig)
        signals.pos_sig.connect(self.on_pos_sig)
        signals.style_sig.connect(self.on_style_sig)
        signals.icon_sig.connect(self.on_icon_sig)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        bg, ring, cursor = self.divide_region()

        # 背景
        painter.save()
        painter.setClipRegion(bg)
        painter.fillRect(bg.boundingRect(), QColor(0, 0, 0, 127))
        painter.restore()
        # 环
        painter.save()
        painter.setClipRegion(ring)
        painter.setBrush(self.ring_back_color)
        painter.drawPie(ring.boundingRect(), 0, 360 * 16)
        painter.setBrush(self.ring_front_color)
        painter.drawPie(ring.boundingRect(), 90, self.ring_deg * 16)
        painter.restore()
        # 指示器
        painter.save()
        painter.setClipRegion(cursor)
        painter.fillRect(cursor.boundingRect(), Qt.transparent)
        painter.restore()

    def divide_region(self):
        cursor_rect = QRect(self.cursor_x - RING_R, self.cursor_y - RING_R, RING_R * 2, RING_R * 2)
        cursor = QRegion(cursor_rect, QRegion.Ellipse)
        tmp = QRegion(cursor_rect.adjusted(-RING_D, -RING_D, RING_D, RING_D), QRegion.Ellipse)
        ring = tmp - cursor
        bg = self.visibleRegion() - tmp
        return bg, ring, cursor

    def on_show_sig(self, is_show):
        self.setWindowOpacity(1 if is_show else 0)

    def on_pos_sig(self, x, y):
        self.cursor_x, self.cursor_y = x * self.screen_width, y * self.screen_height
        self.update()

    def on_style_sig(self, style: RingStyle):
        self.ring_timeline.stop()
        match style:
            case RingStyle.BLUE:
                self.ring_deg = 360
                self.ring_front_color = Qt.blue
                self.ring_back_color = Qt.blue
            case RingStyle.GREEN:
                self.ring_deg = 360
                self.ring_front_color = Qt.green
                self.ring_back_color = Qt.green
            case RingStyle.RED:
                self.ring_deg = 360
                self.ring_front_color = Qt.red
                self.ring_back_color = Qt.red
            case RingStyle.JUDGING:
                self.ring_deg = 0
                self.ring_front_color = Qt.red
                self.ring_back_color = Qt.blue
                self.ring_timeline.start()
            case _:
                self.ring_deg = 360
                self.ring_front_color = Qt.transparent
                self.ring_back_color = Qt.transparent
        self.update()

    def on_frame_changed(self, frame):
        self.ring_deg = frame
        self.update()

    def on_icon_sig(self, gesture: Gesture):
        if gesture is not self.current_gesture:
            self.current_gesture = gesture
            self.setWindowIcon(self.gesture_pix_map[self.current_gesture])


class MyWindowObserver(Observer):

    def __init__(self, window: MyWindow, config: ConfigCenter):
        super().__init__(config)
        self.window = window

    def update(self, key, value):
        if key == 'pause':
            self.window.on_show_sig(not value)
