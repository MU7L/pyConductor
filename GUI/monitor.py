from math import sqrt

import mediapipe as mp
from matplotlib import pyplot as plt
from mediapipe.framework.formats import landmark_pb2

plt.rcParams.update({
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.spines.left': False,
    'axes.spines.bottom': False,
    'xtick.labelbottom': False,
    'xtick.bottom': False,
    'ytick.labelleft': False,
    'ytick.left': False,
    'xtick.labeltop': False,
    'xtick.top': False,
    'ytick.labelright': False,
    'ytick.right': False
})

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


def display_one_image(image, title, subplot, titlesize=16):
    """在图像上显示预测的类别名称和分数"""
    plt.subplot(*subplot)
    plt.imshow(image)
    if len(title) > 0:
        plt.title(title, fontsize=int(titlesize), color='black', fontdict={'verticalalignment': 'center'},
                  pad=int(titlesize / 1.5))
    return subplot[0], subplot[1], subplot[2] + 1


# 图像大小和间距设置
FIGSIZE = 13.0
SPACING = 0.1


def display_batch_of_images_with_gestures_and_hand_landmarks(images, results):
    """显示一批图像，在图像上显示手势类别、置信度、手的关键点"""
    # 将图像数据转换为numpy数组格式
    images = [image.numpy_view() for image in images]
    # 提取手势类别
    gestures = [top_gesture for (top_gesture, _) in results]
    # 提取手的关键点数据
    multi_hand_landmarks_list = [multi_hand_landmarks for (_, multi_hand_landmarks) in results]

    # 自适应方块显示
    rows = int(sqrt(len(images)))
    cols = len(images) // rows

    # TODO
    subplot = (rows, cols, 1)
    if rows < cols:
        plt.figure(figsize=(FIGSIZE, FIGSIZE / cols * rows))
    else:
        plt.figure(figsize=(FIGSIZE / rows * cols, FIGSIZE))

    # 显示手势和手的关键点
    for i, (image, gestures) in enumerate(zip(images[:rows * cols], gestures[:rows * cols])):
        # 标题包括手势类别和置信度
        title = f"{gestures.category_name} ({gestures.score:.2f})"
        # 根据图像大小和标题设置标题文字大小
        dynamic_titlesize = FIGSIZE * SPACING / max(rows, cols) * 40 + 3
        # 复制图像数据
        annotated_image = image.copy()

        # 遍历每张图像中的手的关键点数据，并绘制在图像上
        for hand_landmarks in multi_hand_landmarks_list[i]:
            hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
            hand_landmarks_proto.landmark.extend([
                landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
            ])

            mp_drawing.draw_landmarks(
                annotated_image,
                hand_landmarks_proto,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())

        # 显示一张图像并设置子图编号和标题
        subplot = display_one_image(annotated_image, title, subplot, titlesize=dynamic_titlesize)

    # 布局调整
    plt.tight_layout()
    plt.subplots_adjust(wspace=SPACING, hspace=SPACING)
    # 显示图像
    plt.show()
