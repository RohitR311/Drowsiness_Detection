import cv2
import time
import numpy as np
import mediapipe as mp
from mediapipe.python.solutions.drawing_utils import _normalized_to_pixel_coordinates as denorm_coordinates

def get_mediapipe_app(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
):
    """Initialize and return Mediapipe FaceMesh Solution Graph object"""

    face_mesh = mp.solutions.face_mesh.FaceMesh(
        max_num_faces=max_num_faces,
        refine_landmarks=refine_landmarks,
        min_detection_confidence=min_detection_confidence,
        min_tracking_confidence=min_tracking_confidence,
    )
    return face_mesh

def distance(pt1, pt2):
    dist = sum([(i - j) ** 2 for i, j in zip(pt1, pt2)]) ** 0.5
    return dist


def get_ear(landmarks, refer_idxs, frame_width, frame_height):
    try:
        coords_pts = []
        for i in refer_idxs:
            lm = landmarks[i]
            coord = denorm_coordinates(lm.x, lm.y, frame_width, frame_height)
            coords_pts.append(coord)

        P2_P6 = distance(coords_pts[1], coords_pts[5])
        P3_P5 = distance(coords_pts[2], coords_pts[4])
        P1_P4 = distance(coords_pts[0], coords_pts[3])

        ear = (P2_P6 + P3_P5) / (2.0 * P1_P4)
    except:
        ear = 0.0
        coords_pts = None

    return ear, coords_pts


def calculate_avg_ear(landmarks, left_eye_idxs, right_eye_idxs, image_w, image_h):
    left_ear, left_lm_coords = get_ear(
        landmarks, left_eye_idxs, image_w, image_h)
    right_ear, right_lm_coords = get_ear(
        landmarks, right_eye_idxs, image_w, image_h)

    Avg_EAR = (left_ear + right_ear) / 2.0

    return Avg_EAR, (left_lm_coords, right_lm_coords)




def plot_eye_landmarks(frame, left_lm_coordinates,
                       right_lm_coordinates, color):
    for lm_coordinates in [left_lm_coordinates, right_lm_coordinates]:
        if lm_coordinates:
            for coord in lm_coordinates:
                cv2.circle(frame, coord, 2, color, -1)

    frame = cv2.flip(frame, 1)
    return frame


def plot_text(image, text, origin,
              color, font=cv2.FONT_HERSHEY_SIMPLEX,
              fntScale=0.8, thickness=2
              ):
    image = cv2.putText(image, text, origin, font, fntScale, color, thickness)
    return image


class VideoFrameHandler:

    def __init__(self):
        self.eye_idxs = {
            "left": [362, 385, 387, 263, 373, 380],
            "right": [33, 160, 158, 133, 153, 144],
        }

        self.RED = (0, 0, 255)
        self.GREEN = (0, 255, 0)

        self.facemesh_model = get_mediapipe_app()

        self.state_tracker = {
            "start_time": time.perf_counter(),
            "DROWSY_TIME": 0.0,
            "COLOR": self.GREEN,
            "play_alarm": False,
        }

        self.EAR_txt_pos = (10, 30)

    def process(self, frame: np.array, thresholds: dict):

        frame.flags.writeable = False
        frame_h, frame_w = frame.shape[:2]
        DROWSY_TIME_txt_pos = (10, int(frame_h // 2 * 1.7))
        ALM_txt_pos = (10, int(frame_h // 2 * 1.85))

        results = self.facemesh_model.process(frame)

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
            EAR, coordinates = calculate_avg_ear(
                landmarks, self.eye_idxs["left"], self.eye_idxs["right"], frame_w, frame_h)

            frame = plot_eye_landmarks(frame,
                                       coordinates[0],
                                       coordinates[1],
                                       self.state_tracker["COLOR"]
                                       )

            if EAR < thresholds["EAR_THRESH"]:
                end_time = time.perf_counter()
                self.state_tracker["DROWSY_TIME"] += end_time - \
                    self.state_tracker["start_time"]
                self.state_tracker["start_time"] = end_time
                self.state_tracker["COLOR"] = self.RED

                if self.state_tracker["DROWSY_TIME"] >= thresholds["WAIT_TIME"]:
                    self.state_tracker["play_alarm"] = True
                    plot_text(frame, "WAKE UP! WAKE UP",
                              ALM_txt_pos, self.state_tracker["COLOR"])
            else:
                self.state_tracker["start_time"] = time.perf_counter()
                self.state_tracker["DROWSY_TIME"] = 0.0
                self.state_tracker["COLOR"] = self.GREEN
                self.state_tracker["play_alarm"] = False

            EAR_txt = f"EAR: {round(EAR, 2)}"
            DROWSY_TIME_txt = f"DROWSY: {round(self.state_tracker['DROWSY_TIME'], 3)} Secs"
            plot_text(frame, EAR_txt,
                      self.EAR_txt_pos, self.state_tracker["COLOR"])
            plot_text(frame, DROWSY_TIME_txt,
                      DROWSY_TIME_txt_pos, self.state_tracker["COLOR"])
        else:
            self.state_tracker["start_time"] = time.perf_counter()
            self.state_tracker["DROWSY_TIME"] = 0.0
            self.state_tracker["COLOR"] = self.GREEN
            self.state_tracker["play_alarm"] = False

            frame = cv2.flip(frame, 1)
        return frame, self.state_tracker["play_alarm"]
