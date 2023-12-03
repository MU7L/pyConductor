from enum import Enum


class Signal(Enum):
    NONE = 0
    ONE = 1
    LEFT = 2
    RIGHT = 3
    GRAB = 4


class Report:
    def __init__(self, signal: Signal, x: float, y: float):
        self.signal = signal
        self.x = x
        self.y = y

    def __repr__(self):
        return f'Report(signal={self.signal.name}, x={self.x}, y={self.y})'
