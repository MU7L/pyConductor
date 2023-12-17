from PySide6.QtCore import QObject, Signal

from core.data import Gesture
from views.ring_style import RingStyle


class Signals(QObject):
    show_sig = Signal(bool)
    pos_sig = Signal(float, float)
    style_sig = Signal(RingStyle)
    icon_sig = Signal(Gesture)
