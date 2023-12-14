from os import path

ROOT_PATH = path.dirname(path.dirname(path.abspath(__file__)))

# data path
PNG_PATH = path.join(ROOT_PATH, 'data/png')
ICON_PATH = path.join(ROOT_PATH, 'data/png/ok.png')
TASK_PATH = path.join(ROOT_PATH, 'data/task/gesture_recognizer.task')

# logger
LOG_PATH = path.join(ROOT_PATH, 'logs')

# config center
init_config = {
    'pause': False,  # 暂停
    'cam': 0,  # 相机编号
    'flip': True,  # 镜像
}

# analyzer
DEBOUNCE_DELAY_S = 0.07  # 防抖延时
SMOOTHENING = 5  # 平滑系数

# machine
IDLE_JUDGEMENT_S = 2  # 连续接收PALM一定时间后才进入move状态
ACTIVE_BOUNCE_RANGE = 20  # 抖动范围
ACTIVE_JUDGEMENT_S = 1  # 长按判定时长

# view
FPS = 60  # 刷新率
RING_R = 30  # 半径
RING_D = 5  # 色环宽度
