from time import time

import pyautogui

from GUI.window import MyWindow, RingStyle
from GUI.window2 import MyWidget
from analyzer.core import Gesture, Report
from utils.config import Observer, ConfigCenter
from utils.logger import logger

pyautogui.FAILSAFE = False  # pyautogui 失控时跳出异常
pyautogui.PAUSE = 0  # pyautogui 响应时间

WIDTH, HEIGHT = pyautogui.size()

# TODO: 测试新widget
class Machine:

    def __init__(self, widget: MyWidget, config: ConfigCenter):
        super().__init__()
        self.widget = widget
        self.observer = MachineObserver(self, config)

        # 状态
        self.state_map = {
            'idle': IdleState(self),
            'move': MoveState(self),
            'active': ActiveState(self),
            'drag': DragState(self),
            'scroll': ScrollState(self),
        }

        # 当前状态
        self.state = self.state_map['idle']

    def transition(self, state: str):
        """状态转移"""
        self.state.exit()
        self.state = self.state_map[state]
        self.state.enter()

    def handle(self, report: Report):
        if self.observer.config.get('pause'):
            return
        self.window.set_icon(report.gesture)
        self.state.handle(report)


class MachineObserver(Observer):
    def __init__(self, machine: Machine, config: ConfigCenter):
        super().__init__(config)
        self.machine = machine

    def update(self, key, value):
        if key == 'pause' and value:
            self.machine.transition('idle')


class State:
    """状态抽象类"""

    def __init__(self, machine: Machine):
        self.machine = machine

    def enter(self):
        pass

    def handle(self, report: Report):
        pass

    def exit(self):
        pass


class IdleState(State):
    """该状态下不响应任何手势，除了Gesture.PALM"""
    JUDGEMENT_SECONDS = 2  # 连续接收PALM一定时间后才进入move状态

    def __init__(self, machine: Machine):
        super().__init__(machine)
        self.first_palm_time = None

    def enter(self):
        self.machine.window.hide()
        logger.debug('enter idle state')

    def handle(self, report: Report):
        if report.gesture == Gesture.PALM:
            if self.first_palm_time is None:
                self.first_palm_time = time()
            if time() - self.first_palm_time >= self.JUDGEMENT_SECONDS:
                self.machine.transition('move')
        else:
            self.first_palm_time = None

    def exit(self):
        self.machine.window.show()
        logger.debug('exit idle state')


class MoveState(State):
    """该状态下只响应鼠标位置的移动"""

    def enter(self):
        self.machine.window.set_ring()
        logger.debug('enter move state')

    def handle(self, report: Report):
        x, y = report.x, report.y
        self.machine.window.move_to(x, y)
        match report.gesture:
            case Gesture.NONE:
                self.machine.transition('idle')
            case Gesture.OK:
                self.machine.transition('active')
            case Gesture.FIST:
                self.machine.transition('scroll')
            case _:
                pyautogui.moveTo(x * WIDTH, y * HEIGHT)

    def exit(self):
        logger.debug('exit move state')


class ActiveState(State):
    """该状态下处理单击、长按事件 不响应移动"""
    JUDGEMENT_SECONDS = 1  # 判定时长
    BOUNCE_RANGE = 20  # 抖动范围

    def __init__(self, machine: Machine):
        super().__init__(machine)
        self.x = None
        self.y = None
        self.start_time = None
        self.res = 'left'

    def enter(self):
        self.machine.window.set_ring(RingStyle.JUDGING, self.JUDGEMENT_SECONDS * 1000)
        self.x, self.y = pyautogui.position()
        self.start_time = time()
        logger.debug('enter active state')

    def handle(self, report: Report):
        # 实时显示手的位置
        x, y = report.x, report.y
        self.machine.window.move_to(x, y)
        match report.gesture:
            case Gesture.NONE:
                self.res = 'left'
                self.machine.transition('idle')
            case Gesture.OK:
                # 判定是否超出抖动范围
                _x, _y = x * WIDTH, y * HEIGHT
                if abs(_x - self.x) >= self.BOUNCE_RANGE or abs(_y - self.y) >= self.BOUNCE_RANGE:
                    self.res = 'drag'
                    self.machine.transition('drag')
                # 判定是否为长按
                elif time() - self.start_time >= self.JUDGEMENT_SECONDS:
                    self.res = 'right'
                    self.machine.transition('move')
            case _:
                self.res = 'left'
                self.machine.transition('move')

    def exit(self):
        match self.res:
            case 'left':
                self.machine.window.set_ring(RingStyle.BLUE)
                pyautogui.leftClick()
            case 'right':
                self.machine.window.set_ring(RingStyle.RED)
                pyautogui.rightClick()
            case 'drag':
                pass
        self.x = None
        self.y = None
        self.start_time = None
        self.res = None
        logger.debug('exit active state')


class DragState(State):
    """该状态下处理拖拽事件"""

    def enter(self):
        self.machine.window.set_ring(RingStyle.BLUE)
        pyautogui.mouseDown(button='left')
        logger.debug('enter drag state')

    def handle(self, report: Report):
        x, y = report.x, report.y
        self.machine.window.move_to(x, y)
        match report.gesture:
            case Gesture.NONE:
                self.machine.transition('idle')
            case Gesture.OK:
                pyautogui.moveTo(x * WIDTH, y * HEIGHT)
            case _:
                self.machine.transition('move')

    def exit(self):
        pyautogui.mouseUp(button='left')
        logger.debug('exit drag state')


class ScrollState(State):
    """该状态下处理滑动事件"""

    def __init__(self, machine: Machine):
        super().__init__(machine)
        self.y = None

    def enter(self):
        self.machine.window.set_ring(RingStyle.GREEN)
        self.y = pyautogui.position()[1]
        logger.debug('enter scroll state')

    def handle(self, report: Report):
        x, y = report.x, report.y
        self.machine.window.move_to(x, y)
        _y = y * HEIGHT
        dy = int(_y - self.y)
        pyautogui.scroll(dy)  # Windows 暂不支持左右滑动
        self.y = _y

    def exit(self):
        logger.debug('exit scroll state')
