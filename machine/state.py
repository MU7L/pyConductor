from time import time

import pyautogui

from GUI.window import RingStyle
from machine.machine import Machine

WIDTH, HEIGHT = pyautogui.size()


def get_x_y(x: float, y: float):
    return x * WIDTH, y * HEIGHT


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
    """该状态下不响应任何手势，除了Gesture.PALM"""

    def enter(self):
        self.machine.window.hide()

    def exit(self):
        self.machine.window.showFullScreen()


class MoveState(State):
    """该状态下只响应鼠标位置的移动"""

    def enter(self):
        self.machine.window.set_ring()

    def handle(self, x, y):
        _x, _y = get_x_y(x, y)
        self.machine.window.move_to(x, y)
        pyautogui.moveTo(_x, _y)


class ActiveState(State):
    """该状态下处理单击、长按事件 不响应移动"""
    JUDGEMENT_SECONDS = 1  # 判定时长
    BOUNCE_RANGE = 10  # 抖动范围

    def __init__(self, machine: Machine):
        super().__init__(machine)
        self.x = None
        self.y = None
        self.start_time = None
        self.transited = False

    def enter(self):
        self.x, self.y = pyautogui.position()
        self.start_time = time()
        self.machine.window.set_ring(RingStyle.JUDGING)

    def handle(self, x, y):
        _x, _y = get_x_y(x, y)
        if self.x is None or self.y is None:
            self.x, self.y = _x, _y
        if time() - self.start_time >= self.JUDGEMENT_SECONDS:
            # 若超过指定时间 认定为长按 触发右键单击后退出当前状态
            self.machine.transition_2(self.machine.move_state)
        elif abs(_x - self.x) > self.BOUNCE_RANGE or abs(_y - self.y) > self.BOUNCE_RANGE:
            # 若指定时间内移动范围超出阈值 认定为拖拽 进入drag_state
            self.transited = True
            self.machine.transition_2(self.machine.drag_state)

    def exit(self):
        if not self.transited:
            if time() - self.start_time < self.JUDGEMENT_SECONDS:
                self.machine.window.set_ring(RingStyle.BLUE)
                pyautogui.leftClick()
            else:
                self.machine.window.set_ring(RingStyle.RED)
                pyautogui.rightClick()
        self.x = None
        self.y = None
        self.start_time = None
        self.transited = False


class DragState(State):
    """该状态下处理拖拽事件"""

    def enter(self):
        self.machine.window.set_ring(RingStyle.BLUE)
        pyautogui.mouseDown(button='left')

    def handle(self, x, y):
        _x, _y = get_x_y(x, y)
        pyautogui.moveTo(_x, _y)

    def exit(self):
        pyautogui.mouseUp(button='left')


class ScrollState(State):
    """该状态下处理滑动事件"""

    def enter(self):
        self.machine.window.set_ring(RingStyle.GREEN)

    def handle(self, _, y):
        new_y = y * HEIGHT
        old_y = pyautogui.position()[1]
        dy = int(new_y - old_y)
        pyautogui.scroll(dy)  # Windows 暂不支持左右滑动
