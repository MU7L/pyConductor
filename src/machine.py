from time import time

import pyautogui

from src.core import Signal, Report

# pyautogui.FAILSAFE = True  # 失控时跳出异常
pyautogui.PAUSE = 0  # 响应时间
WIDTH, HEIGHT = pyautogui.size()

JUDGEMENT_TIME = 1  # 判定时间


class Machine:
    def __init__(self):
        super().__init__()

        # 状态
        self.idle_state = IdleState(self)
        self.left_state = LeftState(self)
        self.right_state = RightState(self)
        self.scroll_state = ScrollState(self)

        # 状态转移图
        self.event_map = {
            self.idle_state: {
                Signal.LEFT: self.left_state,
                Signal.RIGHT: self.right_state,
                Signal.GRAB: self.scroll_state,
            },
            self.left_state: {
                Signal.LEFT: self.left_state
            },
            self.right_state: {
                Signal.RIGHT: self.right_state,
            },
            self.scroll_state: {
                Signal.GRAB: self.scroll_state,
            }
        }

        # 当前状态
        self.state = self.idle_state

    def transition(self, signal: Signal):
        """状态转移"""
        next_state = self.event_map.get(self.state).get(signal) or self.idle_state
        if next_state is not self.state:
            self.state.exit()
            self.state = next_state
            self.state.enter()

    def handle(self, report: Report):
        if report.signal is Signal.NONE:
            return
        x = report.x * WIDTH
        y = report.y * HEIGHT
        self.transition(report.signal)
        self.state.handle(x, y)


class State:
    """状态抽象类"""

    def __init__(self, machine: Machine):
        self.machine = machine

    def enter(self):
        pass

    def handle(self, x: float, y: float):
        pass

    def exit(self):
        pass


class IdleState(State):
    """空闲状态：该状态下没有按键按下，只处理鼠标的移动"""

    def handle(self, x, y):
        pyautogui.moveTo(x, y)


class LeftState(State):
    """左键状态：该状态下可能触发左键单击或左键拖动事件"""

    def __init__(self, machine: Machine, judgement_time=JUDGEMENT_TIME):
        super().__init__(machine)
        self.judgement_time = judgement_time
        self.start = None
        self.is_down = False

    def enter(self):
        self.start = time()

    def handle(self, x, y):
        if time() - self.start < self.judgement_time:
            # 判定时间内不响应
            return
        # 超过判定时间 触发拖动
        if not self.is_down:
            pyautogui.mouseDown(button='left')
            self.is_down = True
        pyautogui.moveTo(x, y)

    def exit(self):
        if time() - self.start < self.judgement_time and not self.is_down:
            # 在判定时间内离开此状态时 触发单击
            # TODO: 能否利用GUI提升准确性
            pyautogui.leftClick()
        else:
            # 结束拖动
            pyautogui.mouseUp(button='left')
        self.start = None
        self.is_down = False


class RightState(State):
    """右键状态：该状态下可能触发右键单击事件"""

    def handle(self, x, y):
        pyautogui.moveTo(x, y)

    def exit(self):
        pyautogui.rightClick()


class ScrollState(State):
    def __init__(self, machine: Machine):
        super().__init__(machine)
        self.y = None

    def enter(self):
        _, self.y = pyautogui.position()

    def handle(self, _, y):
        dy = int(y - self.y)
        pyautogui.scroll(dy)  # Windows 暂不支持左右滑动
        self.y = y

    def exit(self):
        self.y = None
