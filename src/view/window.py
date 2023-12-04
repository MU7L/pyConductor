import sys

from PySide6.QtCore import Qt, QTimer, QPointF
from PySide6.QtGui import QColor, QPainter, QGuiApplication, QRadialGradient
from PySide6.QtWidgets import QWidget, QApplication

from src.core import Report, Signal

FPS = 60  # 刷新率
R = 30  # 半径
RING = 5  # 色环宽度


class MyGradient(QRadialGradient):
    """自定义径向渐变"""

    def __init__(self, x, y, r=R, d=RING):
        """
        :param x: 圆心x
        :param y: 圆心y
        :param r: 内径
        :param d: 色环宽度
        """
        super().__init__(x, y, r + d, x, y, r)
        self.setColorAt(0, QColor(0, 0, 0, 0))
        self.setColorAt(1, QColor(0, 0, 0, 127))

    def set_pos(self, x, y):
        p = QPointF(x, y)
        self.setCenter(p)
        self.setFocalPoint(p)

    def set_ring_color(self, color):
        """
        :param color: Qt内置颜色
        """
        self.setColorAt(0.5, QColor(color))

    def __repr__(self):
        return f"MyAnimatedGradient(x={self.center().x()}, y={self.center().y()}"


class MyWindow(QWidget):
    """主界面"""

    def __init__(self):
        super().__init__()
        self.init_ui()

        screen = QGuiApplication.primaryScreen().geometry()
        self.screen_width = screen.width()
        self.screen_height = screen.height()

        self.is_active = False
        self.gradient = MyGradient(self.screen_width / 2, self.screen_height / 2, R, RING)
        self.set_interval()

    def init_ui(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint  # 无边框
            | Qt.WindowStaysOnTopHint  # 置顶
            | Qt.WindowTransparentForInput  # 鼠标穿透
            | Qt.ToolTip  # 无任务栏图标
        )
        self.setAttribute(Qt.WA_TranslucentBackground)  # 透明

    def set_interval(self):
        timer = QTimer(self)
        timer.timeout.connect(self.update)  # 忽略此处报错
        timer.start(int(1000 / FPS))

    def paintEvent(self, event):
        if not self.is_active:
            return
        painter = QPainter(self)
        painter.setBrush(self.gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())

    def handle(self, report: Report):
        if report.signal is Signal.NONE:
            self.is_active = False
            return

        self.is_active = True
        x = report.x * self.screen_width
        y = report.y * self.screen_height
        self.gradient.set_pos(x, y)

        match report.signal:
            case Signal.LEFT:
                self.gradient.set_ring_color(Qt.blue)
            case Signal.GRAB:
                self.gradient.set_ring_color(Qt.green)
            case Signal.RIGHT:
                self.gradient.set_ring_color(Qt.red)
            case _:
                self.gradient.set_ring_color(Qt.black)


if __name__ == '__main__':
    app = QApplication([])
    window = MyWindow()
    window.show()
    sys.exit(app.exec())
