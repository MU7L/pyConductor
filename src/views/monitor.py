import cv2
from mediapipe.framework.formats import landmark_pb2
from mediapipe.python.solutions.drawing_styles import get_default_hand_landmarks_style, \
    get_default_hand_connections_style
from mediapipe.python.solutions.drawing_utils import draw_landmarks
from mediapipe.python.solutions.hands_connections import HAND_CONNECTIONS
from mediapipe.tasks.python.vision import GestureRecognizerResult

landmarks_style = get_default_hand_landmarks_style()
connections_style = get_default_hand_connections_style()
hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()


# TODO: 监测窗口
def show_landmarks(frame, result: GestureRecognizerResult):
    landmarks_proto = landmark_pb2.NormalizedLandmarkList()
    if len(result.hand_landmarks) > 0:
        hand_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in
            result.hand_landmarks[0]
        ])
    draw_landmarks(
        frame,
        landmarks_proto,
        HAND_CONNECTIONS,
        landmarks_style,
        connections_style
    )
    cv2.imshow('test', frame)
    cv2.waitKey(1)
