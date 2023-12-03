from math import sqrt, ceil

from PySide6.QtCore import Qt, QTimer, QPointF, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QPainter, QGuiApplication, QRadialGradient
from PySide6.QtWidgets import QWidget

from src.core import Report, Signal

settings = {
    'fps': 60,
    'ring': 5,
    'min_r': 30
}


class MyWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.init_ui()

        screen = QGuiApplication.primaryScreen().geometry()
        self.screen_width = screen.width()
        self.screen_height = screen.height()
        self.max_r = ceil(sqrt(self.screen_width ** 2 + self.screen_height ** 2))
        self.min_r = settings['min_r']

        self.is_active = False

        r = settings['min_r']
        ring = settings['ring']
        self.gradient = QRadialGradient(0, 0, r + ring, 0, 0, r)
        self.gradient.setColorAt(0, QColor(0, 0, 0, 0))
        self.gradient.setColorAt(1, QColor(0, 0, 0, 127))

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(int(1000 / settings['fps']))

        # TODO: 动画
        # self.enter_animation = QPropertyAnimation(self.gradient, b"centerRadius")
        # self.enter_animation.setEasingCurve(QEasingCurve.InCubic)
        # self.enter_animation.setStartValue(self.max_r)
        # self.enter_animation.setEndValue(self.min_r)
        # self.enter_animation.setDuration(2000)
        #
        # self.leave_animation = QPropertyAnimation(self, b"centerRadius")
        # self.enter_animation.setEasingCurve(QEasingCurve.OutCubic)
        # self.leave_animation.setStartValue(self.min_r)
        # self.leave_animation.setEndValue(self.max_r)
        # self.leave_animation.setDuration(2000)

    def init_ui(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint  # 无边框
            | Qt.WindowStaysOnTopHint  # 置顶
            | Qt.WindowTransparentForInput  # 鼠标穿透
        )
        # 透明
        self.setAttribute(Qt.WA_TranslucentBackground)

    def paintEvent(self, event):
        if not self.is_active:
            return
        painter = QPainter(self)
        painter.setBrush(self.gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())

    def handle(self, report: Report):
        if report.signal is Signal.NONE:
            if self.is_active:
                self.is_active = False
                # self.leave_animation.start()
            return

        if not self.is_active:
            self.is_active = True
            # self.enter_animation.start()
        x = report.x * self.screen_width
        y = report.y * self.screen_height
        p = QPointF(x, y)
        self.gradient.setCenter(p)
        self.gradient.setFocalPoint(p)

        match report.signal:
            case Signal.ONE:
                self.gradient.setColorAt(0.5, QColor(Qt.black))
            case Signal.LEFT:
                self.gradient.setColorAt(0.5, QColor(Qt.blue))
            case Signal.GRAB:
                self.gradient.setColorAt(0.5, QColor(Qt.green))
            case Signal.RIGHT:
                self.gradient.setColorAt(0.5, QColor(Qt.red))
