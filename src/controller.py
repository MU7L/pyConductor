from time import time

import pyautogui

from src.core import Signal, Report

# pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0
width, height = pyautogui.size()

settings = {
    'judge_time': 0.5
}


class Machine:
    def __init__(self):
        super().__init__()

        self.idle_state = IdleState(self)
        self.left_state = LeftState(self)
        self.right_state = RightState(self)
        self.scroll_state = ScrollState(self)
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

        self.state = self.idle_state
        self._x = 0
        self._y = 0

    def getter_x(self):
        return self._x

    def setter_x(self, x):
        self._x = x
        pyautogui.moveTo(self.x, None)

    x = property(getter_x, setter_x)

    def getter_y(self):
        return self._y

    def setter_y(self, y):
        self._y = y
        pyautogui.moveTo(None, self.y)

    y = property(getter_y, setter_y)

    def handle(self, report: Report):
        # if report.signal is Signal.NONE:  # TODO: 为什么没用😠
        if report.signal.value == Signal.NONE.value:
            return
        x = report.x * width
        y = report.y * height
        next_state = self.event_map.get(self.state).get(report.signal) or self.idle_state
        if next_state is not self.state:
            self.state.exit()
            self.state = next_state
            self.state.enter()
        self.state.handle(x, y)


class State:
    def __init__(self, machine: Machine):
        self.machine = machine

    def enter(self):
        pass

    def handle(self, x: float, y: float):
        pass

    def exit(self):
        pass


class IdleState(State):
    def handle(self, x, y):
        self.machine.x = x
        self.machine.y = y


class LeftState(State):
    def __init__(self, machine: Machine):
        super().__init__(machine)
        self.start = None
        self.is_down = False

    def enter(self):
        self.start = time()

    def handle(self, x, y):
        if time() - self.start < settings['judge_time']:  # 判定时间内不响应
            return
        # 拖动
        if not self.is_down:
            pyautogui.mouseDown(button='left')
            self.is_down = True
        self.machine.x = x
        self.machine.y = y

    def exit(self):
        if time() - self.start < settings['judge_time'] and not self.is_down:  # 单击
            pyautogui.leftClick()
        pyautogui.mouseUp(button='left')
        self.start = None
        self.is_down = False


class RightState(State):

    def handle(self, x, y):
        self.machine.x = x
        self.machine.y = y

    def exit(self):
        pyautogui.rightClick()


class ScrollState(State):
    def __init__(self, machine: Machine):
        super().__init__(machine)
        self.y = None

    def enter(self):
        self.y = self.machine.y

    def handle(self, _, y):
        dy = int(y - self.y)
        pyautogui.scroll(dy)
        self.y = y

    def exit(self):
        self.y = None
