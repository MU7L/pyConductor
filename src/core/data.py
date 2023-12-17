import enum


class Gesture(enum.Enum):
    """手势代表信号种类"""
    NONE = 0  # 无手
    PALM = 1  # 检测到手掌表示接管控制
    OK = 2  # 检测到OK表示按下
    FIST = 3  # 检测到握拳表示滑动
    ELSE = 4  # 有手但没定义特殊指令，均认为移动


class Report:
    """数据包"""

    def __init__(self, gesture: Gesture, x: float, y: float):
        self.gesture = gesture
        self.x = x
        self.y = y

    def __repr__(self):
        return f'Report(gesture={self.gesture.name}, x={self.x}, y={self.y})'
