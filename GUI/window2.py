from PySide6.QtCore import Qt, QTimeLine
from PySide6.QtGui import QGuiApplication, QRegion, QPainter
from PySide6.QtWidgets import QWidget

R = 35  # 外径
D = 5  # 色环宽度

ICON_PATH_MAP = {
    'eye': 'resources/png/eye.png',
    'palm': 'resources/png/palm.png',
    'ok': 'resources/png/ok.png',
    'fist': 'resources/png/fist.png',
}


# TODO
class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        screen = QGuiApplication.primaryScreen().geometry()
        self.width = screen.width()
        self.height = screen.height()
        self.init_ui()

        self.deg = 0
        self.front_color = Qt.transparent
        self.back_color = Qt.white
        self.timeline = QTimeLine(4000, self)
        self.timeline.setFrameRange(0, 360)
        self.timeline.frameChanged.connect(self.on_frame_changed)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        rect = self.rect().adjusted(D, D, -D, -D)
        painter.setBrush(self.back_color)
        painter.drawPie(rect, 0, 360 * 16)
        painter.setBrush(self.front_color)
        painter.drawPie(rect, 90 * 16, self.deg % 360 * 16)

    def init_ui(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint  # 去除窗口边框
            | Qt.WindowStaysOnTopHint  # 置顶
            | Qt.WindowTransparentForInput  # 鼠标穿透
        )
        self.setGeometry(self.width / 2, self.height / 2, R * 2, R * 2)

        outer = QRegion(self.rect(), QRegion.Ellipse)
        inner = QRegion(self.rect().adjusted(D, D, -D, -D), QRegion.Ellipse)
        self.setMask(outer - inner)  # 设置窗口形状为椭圆

    def on_frame_changed(self, frame):
        self.deg = frame
        self.update()

    def set_pos(self, x: float, y: float):
        self.move(x * self.width - R / 2, y * self.height - R / 2)

    def set_ring(self, ring: str):
        self.timeline.stop()
        self.deg = 0
        match ring:
            case 'blue':
                self.back_color = Qt.blue
            case 'green':
                self.back_color = Qt.green
            case 'red':
                self.back_color = Qt.red
            case 'judge':
                self.front_color = Qt.red
                self.back_color = Qt.blue
                self.timeline.start()
            case 'hide':
                self.back_color = Qt.transparent
            case _:
                self.back_color = Qt.white
        self.update()
