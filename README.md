# pyConductor - 基于手势识别控制鼠标的软件系统

该项目是由 [MU7L/conductor: gesture recognizer & mouse control (github.com)](https://github.com/MU7L/conductor) 用 Python 改写而来

## 环境依赖

Python 3.11.6

## 实现功能

| 功能   | 手势         |
|------|------------|
| 鼠标移动 | 手移动位置      |
| 左键单击 | 大拇指食指合拢松开  |
| 左键拖动 | 大拇指食指合拢并移动 |
| 右键单击 | 大拇指中指合拢松开  |
| 翻页   | 握拳并上下移动    |

## 技术选型

### 使用 [MediaPipe](https://developers.google.cn/mediapipe/solutions/vision/gesture_recognizer) 实现手势识别

MediaPipe 是一款由 Google Research 开发并开源的多媒体机器学习模型应用框架，MediaPipe 解决方案提供了一些库和工具，可帮助在应用程序中快速应用人工智能 （AI） 和机器学习 （ML） 技术。

通过 OpenCV 读取摄像头数据，获取连续的视频帧，分析视频帧得到手势识别结果。

在本项目中关注手势识别结果中手的位置以及属于何种手势。返回结果数据结构如下（已去除本项目中无关字段）：

``` python
class GestureRecognizerResult:
    """来自 GestureRecognizer 的手势识别结果，其中每个元素表示在图像中检测到的一只手
    Attributes:
        gestures: 识别检测到的手的手势。请注意，手势的索引始终为 -1，因为来自多个手势分类器的原始索引无法合并为有意义的索引
        hand_landmarks: 在归一化图像坐标中检测到的手部特征点
    """

    gestures: List[List[category_module.Category]]
    hand_landmarks: List[List[landmark_module.NormalizedLandmark]]


class Category:
    """分类类别
    Attributes:
        score: 置信度
        category_name: 分类名称
    """

    score: Optional[float] = None
    category_name: Optional[str] = None
    

class NormalizedLandmark:
    """坐标，所有坐标都在 [0,1] 内
    Attributes:
        x / y / z
        visibility: 能见度，坐标可能被遮挡或不在屏幕内
        presence: 坐标是否在屏幕内
    """

    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None
    visibility: Optional[float] = None
    presence: Optional[float] = None
```

其中 `hand_landmarks` 对应下图：

![hand-landmarks](https://developers.google.cn/static/mediapipe/images/solutions/hand-landmarks.png)

### 使用 [PyAutoGUI](https://github.com/asweigart/pyautogui/blob/master/docs/simplified-chinese.ipynb) 实现鼠标控制

PyAutoGUI 允许 Python 脚本控制鼠标和键盘，以自动与其他应用程序进行交互。在本项目中使用状态机设计模式进行包装，实现对鼠标的控制。

### 使用  [PySide6](https://doc.qt.io/qtforpython-6/quickstart.html) 实现应用界面

PySide6 是一个用于 Python 的 Qt 库，它提供了对 Qt 框架的访问。Qt 是一个流行的跨平台 C++ 图形用户界面 (GUI) 库，而 PySide6 则是它的 Python 封装版本。通过使用 PySide6，Python 开发者可以利用 Qt 提供的强大功能来创建丰富的桌面应用和图形界面。在本项目用于中实现设置菜单、视觉效果等功能

## 目录结构

```
pyCnductor
├─resources  # 资源目录，放置识别模型、图标等文件
├─src
│  ├─view          # GUI 相关包
│  │  ├─tray.py    # 托盘
│  │  └─window.py  # 用户界面
│  ├─config.py     # 全局设置模块
│  ├─controller.py # 鼠标控制模块
│  ├─core.py       # 项目自定义核心数据结构
│  ├─utils.py      # 工具类
│  └─vision_task   # 识别模块
├─main.py  # 入口文件
├─requirements.txt  # 依赖项
├─README.md
└─setup.py
```

## 问题记录

1. 设置透明时窗口全黑

   在 Windows 环境下需先设置无边框。

   ```
   self.setWindowFlags(Qt.FramelessWindowHint)     # 无边框
   self.setAttribute(Qt.WA_TranslucentBackground)  # 透明
   ```

2. 实现“半透明窗口，鼠标位置处透明”的方法

   开发过程中尝试了两种实现，最终选择后者。

   1. 通过 QTimer 实现实时重绘窗口，重写 `paintEvent` 方法。在重绘方法中，根据鼠标位置创建圆形区域（QRegion），与窗口区域做布尔运算，对运算得到的区域填充半透明色。
   2. 通过 QTimer 实现实时重绘窗口，重写 `paintEvent` 方法。创建径向渐变（QRadialGradient），在重绘方法中，根据鼠标位置修改径向渐变的中心和焦点，根据手势行为修改焦点处颜色，再填充整个窗口。

3. 怎么区分“左键单击”和“左键拖动”

   在状态机设计中，`LeftState` 在进入状态时会启动计时器，在预定时间内如果接收到非 `Signal.LEFT` 信号，则判定为点击。

4. `if report.signal is Signal.NONE` 判断失效

   该问题原因未查明，后续也未复现。前期解决办法为判断值是否相同

   ``` python
   if report.signal.value == Signal.NONE.value:
       pass
   ```

5.  怎么平滑手势检测结果的抖动

   算法来源：[【教程】AI虚拟鼠标 | MediaPipe OpenCV Python | 计算机视觉]( https://www.bilibili.com/video/BV1z54y157dp)

   详见 `src.utils.Smoothen`

6. 如何获取全部可用摄像头

   在 Python 3.6, 3.7, 3.8, 3.9, 3.10 版本下可以使用 pycameralist 库实现。参考：[python获取所有可用摄像头(id + 名称)可用于opencv_opencv获取摄像头列表-CSDN博客](https://blog.csdn.net/babybin/article/details/122044565)

   本项目使用 Python 3.11.6，不适用以上方法。通过遍历所有摄像头，尝试能否启动来解决该问题。详见 `src.utils.enumerate_devices`

7. 手势识别模块运行在另一个进程，如何控制其参数修改、重启

   由于进程之间不共享内存，无法直接修改参数，采用重启进程的方法解决。由于通过 `multiprocessing.Process` 创建的进程结束后不能再启动，创建一个代理类，每次启动进程前创建一个新进程。详见 `src.vision_task.VisionTask`

8. 主进程中启用接收线程，怎么控制线程终止

   `threading.Thread` 没有提供直接的终止线程的方法，通过设置结束信号（`threading.Event`）间接结束线程

## 版本更新

### 2023/11/27

- 创建项目

### 2023/12/03

- 第一次提交
- 完成大部分功能

### 2023/12/04

- 实现鼠标追踪的视觉效果
- 待解决：实现动态缩放系数
- 待解决：手势识别可视化
- 待解决：解决误判问题（设置启动延迟）
