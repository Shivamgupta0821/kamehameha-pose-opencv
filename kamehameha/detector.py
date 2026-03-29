import math
from collections import deque


WRIST = 0
MIDDLE_MCP = 9


def get_point(landmarks, idx):
    lm = landmarks.landmark[idx]
    return (lm.x, lm.y, lm.z)


def distance_2d(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def hand_center(landmarks):
    wrist = get_point(landmarks, WRIST)
    mid = get_point(landmarks, MIDDLE_MCP)
    return (
        (wrist[0] + mid[0]) / 2,
        (wrist[1] + mid[1]) / 2,
        (wrist[2] + mid[2]) / 2,
    )


class GestureDetector:
    def __init__(self):
        self.history = deque(maxlen=10)
        self.charge_frames = 0
        self.prev_z = None
        self.prev_separation = 0

        # Robustness
        self.missing_frames = 0
        self.last_center = (0.5, 0.5)

        #  Prevent double firing
        self.fire_cooldown = 0

    def detect(self, multi_hand_landmarks):

        result = {
            'hands_detected': 0,
            'charging_pose': False,
            'fire_gesture': False,
            'center': (0.5, 0.5),
            'separation': 0.0,
        }

        #  Cooldown update
        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1

        #  No hands
        if not multi_hand_landmarks:
            self.history.clear()
            self.charge_frames = 0
            self.prev_z = None
            self.prev_separation = 0
            return result

        result['hands_detected'] = len(multi_hand_landmarks)

        #  Allow temporary loss of one hand
        if len(multi_hand_landmarks) < 2:
            self.missing_frames += 1

            if self.missing_frames < 10:
                result['charging_pose'] = self.charge_frames > 3
                result['center'] = self.last_center
                return result
            else:
                self.history.clear()
                self.charge_frames = 0
                return result
        else:
            self.missing_frames = 0

        lm1 = multi_hand_landmarks[0]
        lm2 = multi_hand_landmarks[1]

        # Compute centers
        c1 = hand_center(lm1)
        c2 = hand_center(lm2)

        center_x = (c1[0] + c2[0]) / 2
        center_y = (c1[1] + c2[1]) / 2
        result['center'] = (center_x, center_y)

        #  store last valid center
        self.last_center = (center_x, center_y)

        # Charging logic
        dist = distance_2d(c1, c2)
        aligned = abs(c1[0] - c2[0]) < 0.2
        is_cupped_now = dist < 0.25 and aligned

        if is_cupped_now:
            self.charge_frames += 1
        else:
            self.charge_frames = 0

        result['charging_pose'] = self.charge_frames > 3

        #  FIRE DETECTION

        separation = abs(c1[0] - c2[0])
        result['separation'] = separation

        z1 = c1[2]
        z2 = c2[2]
        current_z = (z1 + z2) / 2

        z_movement = 0
        if self.prev_z is not None:
            z_movement = self.prev_z - current_z

        separation_increase = separation - self.prev_separation

        #  FINAL FIRE CONDITION + COOLDOWN
        if self.fire_cooldown == 0 and (
            (result['charging_pose'] or self.charge_frames > 3)
            and (z_movement > 0.006 or separation_increase > 0.05)
        ):
            result['fire_gesture'] = True
            self.fire_cooldown = 20   # ~0.6 sec cooldown
            self.charge_frames = 0    # reset charge after firing

        # Debug
        print(
            "Z:", round(z_movement, 4),
            "Sep:", round(separation, 3),
            "ΔSep:", round(separation_increase, 3)
        )

        # Update memory
        self.prev_z = current_z
        self.prev_separation = separation

        return result