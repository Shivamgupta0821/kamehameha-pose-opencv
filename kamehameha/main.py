import cv2
import mediapipe as mp
import numpy as np

from state import KamehamehaState
from detector import GestureDetector
from renderer import (
    draw_energy_ball,
    draw_beam,
    apply_screen_flash,
    draw_hud,
)


# ── MediaPipe setup ──────────────────────────────────────────────────────────
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

HAND_LANDMARK_STYLE = mp_drawing.DrawingSpec(color=(100, 200, 255), thickness=1, circle_radius=2)
HAND_CONNECTION_STYLE = mp_drawing.DrawingSpec(color=(60, 120, 200), thickness=1)


def normalized_to_pixel(nx, ny, frame_w, frame_h):
    """Convert MediaPipe normalized (0–1) coords to pixel coords."""
    return int(nx * frame_w), int(ny * frame_h)


def main():
    # Initialize state machine and gesture detector
    state = KamehamehaState()
    detector = GestureDetector()

    # Open webcam (device 0 = default camera)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: Cannot open webcam. Check that a camera is connected.")
        return

    # Request 30 FPS from webcam
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print("Kamehameha Detector running. Press Q or ESC to quit, R to reset.")

    # Run MediaPipe Hands
    with mp_hands.Hands(
        model_complexity=0,         # 0 = lite (fastest), 1 = full
        max_num_hands=2,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.5,
    ) as hands:

        while True:
            ret, frame = cap.read()
            if not ret:
                print("ERROR: Failed to read frame from webcam.")
                break

            # Mirror the frame so it feels like a mirror (selfie view)
            frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]

            # ── Step 1: MediaPipe hand detection ────────────────────────────
            # Convert BGR → RGB for MediaPipe
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb.flags.writeable = False
            results = hands.process(rgb)
            rgb.flags.writeable = True

            # ── Step 2: Draw hand landmarks ──────────────────────────────────
            if results.multi_hand_landmarks:
                for hand_lm in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        frame,
                        hand_lm,
                        mp_hands.HAND_CONNECTIONS,
                        HAND_LANDMARK_STYLE,
                        HAND_CONNECTION_STYLE,
                    )

            # ── Step 3: Gesture detection ────────────────────────────────────
            gesture = detector.detect(results.multi_hand_landmarks)

            # Convert normalized center to pixel coords
            cx_norm, cy_norm = gesture['center']
            center_px = normalized_to_pixel(cx_norm, cy_norm, w, h)

            # Update the state machine with this frame's gesture result
            _update_state(state, gesture, center_px)

            # Advance time-based animations in state
            state.update()

            # ── Step 4: Render effects ────────────────────────────────────────
            if state.current in (state.CHARGING, state.CHARGED):
                draw_energy_ball(frame, state.hand_center, state.charge_level)

            if state.current == state.FIRING:
                apply_screen_flash(frame, state.flash_intensity)
                frame[:] = cv2.add(frame, 50)
                draw_beam(frame, state.hand_center, state.beam_progress)

            # HUD overlay
            draw_hud(frame, state.get_display_info(), gesture['hands_detected'])

            # ── Step 5: Display ──────────────────────────────────────────────
            cv2.imshow("Kamehameha Detector", frame)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord('q'), 27):   # Q or ESC
                break
            elif key == ord('r'):        # R = manual reset
                state.transition_to(state.IDLE)
                detector.__init__()
                print("State reset to IDLE.")

    cap.release()
    cv2.destroyAllWindows()
    print("Exited cleanly.")


def _update_state(state: KamehamehaState, gesture: dict, center_px: tuple):
    current = state.current

    # Always update hand center while visible (used as beam origin)
    if gesture['hands_detected'] >= 2:
        state.hand_center = center_px

    if current == state.IDLE:
        if gesture['charging_pose']:
            state.transition_to(state.CHARGING)

    elif current == state.CHARGING:
        #  PRIORITY: FIRE FIRST
        if gesture['fire_gesture']:
            state.transition_to(state.FIRING)
        #  Only go idle if charge is very low
        elif not gesture['charging_pose'] and state.charge_level < 0.3:
            state.transition_to(state.IDLE)
        # State auto-transitions to CHARGED in state.update() when full

    elif current == state.CHARGED:
        if gesture['fire_gesture']:
            state.transition_to(state.FIRING)
        elif not gesture['charging_pose']:
            # User dropped pose without firing
            state.transition_to(state.IDLE)

    elif current == state.FIRING:
        # State auto-transitions back to IDLE in state.update() when beam finishes
        pass


if __name__ == "__main__":
    main()
