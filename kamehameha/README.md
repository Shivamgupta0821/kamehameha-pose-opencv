# Kamehameha Real-Time Detector
**Dragon Ball Z Kamehameha pose detector using Python + OpenCV + MediaPipe**

---

## How It Works

| State | What you do | What happens on screen |
|-------|-------------|------------------------|
| IDLE | Nothing | Live webcam feed |
| CHARGING | Cup both hands together, palms facing camera | Energy ball appears and grows between your hands |
| CHARGED | Hold the pose for ~2.5 seconds | Ball is fully bright and electric arcs spark |
| FIRING | Push both hands forward OR spread them apart quickly | Screen flashes white, beam shoots across the frame |

---

## Setup

**1. Install Python 3.9+** (check: `python --version`)

**2. Install dependencies:**
```bash
pip install -r requirements.txt
```

**3. Run:**
```bash
python main.py
```

**Controls:**
- `Q` or `ESC` — quit
- `R` — reset state to IDLE

---

## File Structure

```
kamehameha/
  main.py        ← entry point, webcam loop + wiring
  detector.py    ← hand pose & gesture detection logic
  renderer.py    ← energy ball and beam drawing functions
  state.py       ← state machine (IDLE → CHARGING → CHARGED → FIRING)
  requirements.txt
  README.md
```

---

## Tips for Best Results

- **Lighting**: Make sure your hands are well-lit. Dark rooms reduce detection accuracy.
- **Background**: Plain backgrounds work best for MediaPipe hand tracking.
- **Distance**: Keep your hands roughly 40–70cm from the camera.
- **Charging pose**: Cup hands together vertically (one above the other), palms facing the webcam.
- **Fire gesture**: From the charged pose, quickly spread your hands apart horizontally — like a release.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `Cannot open webcam` | Check another app isn't using your camera. Try changing `VideoCapture(0)` to `VideoCapture(1)` |
| Charging pose not detected | Make sure both hands are visible, close together, palms facing camera |
| Beam doesn't fire | After CHARGED, spread your hands apart quickly (> 12% of frame width in one motion) |
| Low FPS | Lower webcam resolution or switch to `model_complexity=0` (already default) |
