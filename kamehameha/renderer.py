import cv2
import numpy as np
import random
import math


def draw_energy_ball(frame, center_px, charge_level):
    if charge_level <= 0.01:
        return

    cx, cy = int(center_px[0]), int(center_px[1])
    cx += random.randint(-2, 2)
    cy += random.randint(-2, 2)

    # Base radius: 20px at 0% → 80px at 100%
    base_radius = int(20 + charge_level * 60)

    # Random flicker: +/- 3px
    flicker = random.randint(-3, 3)
    core_radius = max(5, base_radius + flicker)
    #  ADD PULSE EFFECT
    pulse = int(6 * math.sin(charge_level * 15))
    core_radius += pulse

    # At charge 0: (200, 200, 220) faint bluish white
    # At charge 1: (255, 255, 255) with blue glow
    core_brightness = int(180 + charge_level * 75)
    blue_tint = min(255, int(200 + charge_level * 55))

    # Create overlay canvas (same size as frame)
    h, w = frame.shape[:2]
    overlay = np.zeros((h, w, 3), dtype=np.uint8)

    # --- Draw glow rings (outermost to innermost) ---
    # Each ring is bigger, dimmer. We blend them onto the overlay.
    glow_layers = [
        (core_radius * 4, 0.04),   # very wide, very faint halo
        (core_radius * 3, 0.08),
        (core_radius * 2, 0.15),
        (int(core_radius * 1.5), 0.25),
        (core_radius, 0.6),         # main glow ring
    ]

    for radius, alpha_factor in glow_layers:
        if radius <= 0:
            continue
        # Glow color: mostly blue-white
        glow_color = (
            int(core_brightness * 0.85),   # B
            int(core_brightness * 0.92),   # G
            blue_tint,                      # R (most intense = blue channel in BGR)
        )
        glow_layer = np.zeros_like(overlay)
        cv2.circle(glow_layer, (cx, cy), radius, glow_color, -1)
        # Blend this glow ring onto overlay
        overlay = cv2.addWeighted(overlay, 1.0, glow_layer, alpha_factor, 0)

    # --- Draw solid bright core ---
    core_color = (255, 255, 255)  # pure white core
    cv2.circle(overlay, (cx, cy), max(4, core_radius // 2), core_color, -1)

    # Add tiny bright white sparkle at center
    cv2.circle(overlay, (cx, cy), max(2, core_radius // 5), (255, 255, 255), -1)

    # Blend the entire overlay onto the frame
    # Alpha scales with charge so it fades in naturally
    blend_alpha = min(1.0, 0.5 + charge_level * 0.8)
    overlay=cv2.GaussianBlur(overlay,(0,0),10)
    cv2.addWeighted(frame, 1.0, overlay, blend_alpha, 0, frame)

    # Optional: draw pulsing electric arcs around ball at high charge
    if charge_level > 0.7:
        _draw_electric_arcs(frame, cx, cy, core_radius, charge_level)


def _draw_electric_arcs(frame, cx, cy, radius, charge_level):
    """Draw small lightning-like arcs around the energy ball at high charge."""
    num_arcs = int(charge_level * 6)
    for _ in range(num_arcs):
        angle = random.uniform(0, 2 * math.pi)
        # Arc starts at ball edge
        start_x = int(cx + radius * math.cos(angle))
        start_y = int(cy + radius * math.sin(angle))
        # Arc ends a bit further out with jitter
        end_dist = radius + random.randint(10, 25)
        jitter_angle = angle + random.uniform(-0.4, 0.4)
        end_x = int(cx + end_dist * math.cos(jitter_angle))
        end_y = int(cy + end_dist * math.sin(jitter_angle))

        arc_color = (255, 255, 220)  # bright white-yellow
        cv2.line(frame, (start_x, start_y), (end_x, end_y), arc_color, 1, cv2.LINE_AA)


def draw_beam(frame, origin_px, beam_progress, direction='right'):
    if beam_progress <= 0.0:
        return

    h, w = frame.shape[:2]
    ox, oy = int(origin_px[0]), int(origin_px[1])
    oy+=random.randint(-3,3)

    overlay = np.zeros((h, w, 3), dtype=np.uint8)
    #  Explosion burst at origin
    burst = np.zeros_like(overlay)
    cv2.circle(burst, (ox, oy), 70, (255, 255, 255), -1)
    burst = cv2.GaussianBlur(burst, (0, 0), 15)
    overlay = cv2.addWeighted(overlay, 1.0, burst, 0.6, 0)

    # How far the beam tip has traveled across the screen
    beam_tip_x = int(ox + beam_progress * (w - ox + 100))

    # Beam height (thickness): starts narrow, expands slightly
    beam_half_height = int(35 + beam_progress * 20)

    # Clamp coordinates
    x1 = max(0, ox - 20)
    x2 = min(w, beam_tip_x)
    y1 = max(0, oy - beam_half_height)
    y2 = min(h, oy + beam_half_height)

    if x2 <= x1:
        return

    # --- Draw glow layers ---
    # Wide outer glow
    glow_y_outer = beam_half_height + 30
    outer_y1 = max(0, oy - glow_y_outer)
    outer_y2 = min(h, oy + glow_y_outer)
    glow_outer = np.zeros_like(overlay)
    cv2.rectangle(glow_outer, (x1, outer_y1), (x2, outer_y2), (255,180,80), -1)
    overlay = cv2.addWeighted(overlay, 1.0, glow_outer, 0.12, 0)

    # Mid glow
    glow_y_mid = beam_half_height + 10
    mid_y1 = max(0, oy - glow_y_mid)
    mid_y2 = min(h, oy + glow_y_mid)
    glow_mid = np.zeros_like(overlay)
    cv2.rectangle(glow_mid, (x1, mid_y1), (x2, mid_y2), (160, 200, 255), -1)
    overlay = cv2.addWeighted(overlay, 1.0, glow_mid, 0.25, 0)

    # Core beam
    core_layer = np.zeros_like(overlay)
    cv2.rectangle(core_layer, (x1, y1), (x2, y2), (255, 255, 255), -1)
    overlay = cv2.addWeighted(overlay, 1.0, core_layer, 0.85, 0)

    # Inner bright white strip
    inner_y1 = max(0, oy - beam_half_height // 3)
    inner_y2 = min(h, oy + beam_half_height // 3)
    cv2.rectangle(overlay, (x1, inner_y1), (x2, inner_y2), (255, 255, 255), -1)

    # Blend onto frame
    overlay = cv2.GaussianBlur(overlay, (0, 0), 8)
    cv2.addWeighted(frame, 1.0, overlay, 0.9, 0, frame)

    # Draw origin burst circle
    burst_radius = int(beam_half_height * 1.2)
    burst_overlay = np.zeros_like(frame)
    cv2.circle(burst_overlay, (ox, oy), burst_radius, (200, 220, 255), -1)
    cv2.addWeighted(frame, 1.0, burst_overlay, 0.4, 0, frame)


def apply_screen_flash(frame, flash_intensity):
    if flash_intensity <= 0.0:
        return
    white = np.full_like(frame, 255)
    cv2.addWeighted(frame, 1.0 - flash_intensity, white, flash_intensity, 0, frame)


def draw_hud(frame, state_info, hands_detected):
    h, w = frame.shape[:2]

    # Semi-transparent black bar at top
    bar = frame[0:50, :].copy()
    frame[0:50, :] = (bar * 0.5).astype(np.uint8)

    cv2.putText(frame, state_info, (12, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 1, cv2.LINE_AA)

    cv2.putText(frame, f"Hands: {hands_detected}", (w - 140, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 220, 255), 1, cv2.LINE_AA)

    # Hint at bottom
    hints = {
        'IDLE': "Cup both hands together to charge",
        'CHARGING': "Hold position... charging!",
        'CHARGED': "READY! Push hands forward or spread apart to FIRE",
        'FIRING': "KAMEHAMEHA!!!",
    }
    state_key = state_info.split(":")[1].strip().split(" ")[0] if ":" in state_info else "IDLE"
    hint = hints.get(state_key, "")
    if hint:
        cv2.putText(frame, hint, (12, h - 16),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 230, 255), 1, cv2.LINE_AA)
