import time

import pyautogui

from core.data import Gesture, Report
from core.job import Job
from settings import ACTIVE_BOUNCE_RANGE, ACTIVE_JUDGEMENT_S, IDLE_JUDGEMENT_S

from utils.config import ConfigCenter
from utils.log import logger
from views.ring_style import RingStyle
from worker.signals import Signals

pyautogui.FAILSAFE = False  # pyautogui 失控时跳出异常
pyautogui.PAUSE = 0  # pyautogui 响应时间
WIDTH, HEIGHT = pyautogui.size()


class Machine(Job):
    """状态机"""

    def __init__(self, config: ConfigCenter, signals: Signals):
        super().__init__(config)
        self.signals = signals

        # 状态
        self.state_map = {
            'idle':   IdleState(self),
            'move':   MoveState(self),
            'active': ActiveState(self),
            'drag':   DragState(self),
            'scroll': ScrollState(self),
        }

        # 当前状态
        self.state = self.state_map['idle']

    def process(self, report: Report):
        self.signals.icon_sig.emit(report.gesture)
        self.signals.pos_sig.emit(report.x, report.y)
        report.x *= WIDTH
        report.y *= HEIGHT
        self.state.handle(report)

    def transition(self, state: str):
        """状态转移"""
        self.state.exit()
        self.state = self.state_map[state]
        self.state.enter()

    def update(self, key, value):
        if key == 'pause' and value:
            self.transition('idle')


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

    def __init__(self, machine: Machine):
        super().__init__(machine)
        self.first_time = None

    def enter(self):
        self.machine.signals.style_sig.emit(RingStyle.DEFAULT)
        self.machine.signals.show_sig.emit(False)
        logger.debug('enter idle state')

    def handle(self, report: Report):
        if report.gesture is Gesture.PALM:
            if self.first_time is None:
                self.first_time = time.time()
            if time.time() - self.first_time >= IDLE_JUDGEMENT_S:
                self.machine.transition('move')
        else:
            self.first_time = None

    def exit(self):
        self.machine.signals.show_sig.emit(True)
        logger.debug('exit idle state')


class MoveState(State):
    """该状态下只响应鼠标位置的移动"""

    def enter(self):
        self.machine.signals.style_sig.emit(RingStyle.DEFAULT)
        logger.debug('enter move state')

    def handle(self, report: Report):
        match report.gesture:
            case Gesture.NONE:
                self.machine.transition('idle')
            case Gesture.OK:
                self.machine.transition('active')
            case Gesture.FIST:
                self.machine.transition('scroll')
            case _:
                pyautogui.moveTo(report.x, report.y)

    def exit(self):
        logger.debug('exit move state')


class ActiveState(State):
    """该状态下处理单击、长按事件 不响应移动"""

    def __init__(self, machine: Machine):
        super().__init__(machine)
        self.x = None
        self.y = None
        self.start_time = None
        self.res = None

    def enter(self):
        self.machine.signals.style_sig.emit(RingStyle.JUDGING)
        self.x, self.y = pyautogui.position()
        self.start_time = time.time()
        logger.debug('enter active state')

    def handle(self, report: Report):
        # 实时显示手的位置
        match report.gesture:
            case Gesture.NONE:
                self.res = None
                self.machine.transition('idle')
            case Gesture.OK:
                # 判定是否超出抖动范围
                x, y = report.x, report.y
                if abs(x - self.x) >= ACTIVE_BOUNCE_RANGE or abs(y - self.y) >= ACTIVE_BOUNCE_RANGE:
                    self.res = 'drag'
                    self.machine.transition('drag')
                # 判定是否为长按
                elif time.time() - self.start_time >= ACTIVE_JUDGEMENT_S:
                    self.res = 'right'
                    self.machine.transition('move')
            case _:
                self.res = 'left'
                self.machine.transition('move')

    def exit(self):
        match self.res:
            case 'left':
                self.machine.signals.style_sig.emit(RingStyle.BLUE)
                pyautogui.leftClick()
            case 'right':
                self.machine.signals.style_sig.emit(RingStyle.RED)
                pyautogui.rightClick()
        self.x = None
        self.y = None
        self.start_time = None
        self.res = None
        logger.debug('exit active state')


class DragState(State):
    """该状态下处理拖拽事件"""

    def enter(self):
        self.machine.signals.style_sig.emit(RingStyle.BLUE)
        pyautogui.mouseDown(button='left')
        logger.debug('enter drag state')

    def handle(self, report: Report):
        match report.gesture:
            case Gesture.NONE:
                self.machine.transition('idle')
            case Gesture.OK:
                pyautogui.moveTo(report.x, report.y)
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
        self.machine.signals.style_sig.emit(RingStyle.GREEN)
        self.y = pyautogui.position()[1]
        logger.debug('enter scroll state')

    def handle(self, report: Report):
        match report.gesture:
            case Gesture.NONE:
                self.machine.transition('idle')
            case Gesture.FIST:
                dy = int(report.y - self.y)
                pyautogui.scroll(dy)  # Windows 暂不支持左右滑动
                self.y = report.y
            case _:
                self.machine.transition('move')

    def exit(self):
        self.y = None
        logger.debug('exit scroll state')
