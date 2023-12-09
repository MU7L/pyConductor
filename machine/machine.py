import pyautogui

from GUI.window import MyWindow
from analyzer.core import Gesture, Report
from machine.state import IdleState, MoveState, ActiveState, DragState, ScrollState
from utils.config import Observer, ConfigCenter

pyautogui.FAILSAFE = False  # 失控时跳出异常
pyautogui.PAUSE = 0  # 响应时间


class Machine:
    def __init__(self, window: MyWindow, config: ConfigCenter):
        super().__init__()
        self.window = window
        self.observer = MachineObserver(self, config)

        # 状态
        self.idle_state = IdleState(self)
        self.move_state = MoveState(self)
        self.active_state = ActiveState(self)
        self.drag_state = DragState(self)
        self.scroll_state = ScrollState(self)

        # 状态转移图
        self.event_map = {
            self.idle_state: {
                Gesture.PALM: self.move_state,
            },
            self.move_state: {
                Gesture.NONE: self.idle_state,
                Gesture.OK: self.active_state,
                Gesture.FIST: self.scroll_state,
            },
            self.active_state: {
                Gesture.NONE: self.idle_state,
                Gesture.PALM: self.move_state,
                Gesture.FIST: self.move_state,
                Gesture.ELSE: self.move_state,
            },
            self.drag_state: {
                Gesture.NONE: self.idle_state,
                Gesture.PALM: self.move_state,
                Gesture.FIST: self.move_state,
                Gesture.ELSE: self.move_state,
            },
            self.scroll_state: {
                Gesture.NONE: self.idle_state,
                Gesture.PALM: self.move_state,
                Gesture.OK: self.move_state,
                Gesture.ELSE: self.move_state,
            }
        }

        # 当前状态
        self.state = self.idle_state

    def transition(self, gesture: Gesture):
        """状态转移"""
        next_state = self.event_map.get(self.state).get(gesture)
        # 未定义的事件均不响应，维持当前状态
        if next_state is not None and self.state is not next_state:
            self.state.exit()
            self.state = next_state
            self.state.enter()

    def transition_2(self, next_state):
        """直接状态转移"""
        self.state.exit()
        self.state = next_state
        self.state.enter()

    def handle(self, report: Report):
        if self.observer.config.get('pause'):
            return
        self.transition(report.gesture)
        self.state.handle(report.x, report.y)


class MachineObserver(Observer):
    def __init__(self, machine: Machine, config: ConfigCenter):
        super().__init__(config)
        self.machine = machine

    def update(self, key, value):
        if key == 'pause':
            if value:
                self.machine.transition_2(self.machine.idle_state)
