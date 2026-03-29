import time
class KamehamehaState:
    IDLE = "IDLE"
    CHARGING = "CHARGING"
    CHARGED = "CHARGED"
    FIRING = "FIRING"

    def __init__(self):
        self.current = self.IDLE

        # Charging progress: 0.0 → 1.0
        self.charge_level = 0.0
        self.charge_start_time = None
        self.charge_duration = 1.8  # seconds to fully charge

        # Beam animation progress: 0.0 → 1.0
        self.beam_progress = 0.0
        self.beam_start_time = None
        self.beam_duration = 3.0  # seconds for beam to cross screen

        # Flash effect on fire
        self.flash_intensity = 0.0  # 0.0 = no flash, 1.0 = full white

        # Store last known hand center for beam origin
        self.hand_center = (320, 240)

    def transition_to(self, new_state):
        """Move to a new state and reset relevant timers."""
        prev = self.current
        self.current = new_state

        if new_state == self.CHARGING:
            if prev != self.CHARGING:
                self.charge_start_time = time.time()
                self.charge_level = 0.0

        elif new_state == self.CHARGED:
            self.charge_level = 1.0

        elif new_state == self.FIRING:
            self.beam_start_time = time.time()
            self.beam_progress = 0.0
            self.flash_intensity = 1.0  # trigger full flash

        elif new_state == self.IDLE:
            self.charge_level = 0.0
            self.charge_start_time = None
            self.beam_progress = 0.0

    def update(self):
        """Called every frame to advance time-based animations."""
        now = time.time()

        if self.current == self.CHARGING and self.charge_start_time:
            elapsed = now - self.charge_start_time
            progress = elapsed / self.charge_duration
            self.charge_level = min(progress ** 1.5,1.0)
            # Auto-transition to CHARGED when fully charged
            if self.charge_level >= 1.0:
                self.transition_to(self.CHARGED)

        elif self.current == self.FIRING and self.beam_start_time:
            elapsed = now - self.beam_start_time
            self.beam_progress = min(elapsed / self.beam_duration, 1.0)
            # Decay flash quickly (first 0.3 seconds)
            self.flash_intensity = max(0.0, 1.0 - (elapsed / 0.2))
            # Return to IDLE when beam animation finishes
            if self.beam_progress >= 1.0:
                self.transition_to(self.IDLE)

        elif self.current == self.IDLE:
            # Decay charge level when not charging (quick drop)
            decay = 0.08
            self.charge_level = max(0.0, self.charge_level - decay)

    def get_display_info(self):
        """Returns a string summary for debug overlay on frame."""
        info = f"State: {self.current}"
        if self.current in (self.CHARGING, self.CHARGED):
            info += f"  |  Charge: {int(self.charge_level * 100)}%"
        elif self.current == self.FIRING:
            info += f"  |  Beam: {int(self.beam_progress * 100)}%"
        return info
