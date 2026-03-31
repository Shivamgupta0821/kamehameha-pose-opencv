# Kamehameha Gesture Recognition System

## Overview

This project is a real-time computer vision application that detects hand gestures using MediaPipe and simulates a Kamehameha-style energy attack using OpenCV. It combines gesture recognition, state-driven interaction, and layered visual effects to create an interactive experience using a webcam.

The system processes live video input, identifies hand positions, and triggers animations such as an energy ball and beam based on user gestures.


## Features

- Real-time hand tracking using MediaPipe (21 landmarks per hand)
- Charging pose detection (hands held together)
- Firing gesture detection:
  - Forward push (Z-axis movement)
  - Sudden horizontal hand separation
- Animated energy ball with glow, pulse, and flicker effects
- Beam rendering with layered glow and screen flash
- Robust gesture handling:
  - Works even if one hand temporarily disappears
  - Prevents double firing using cooldown logic
- State machine for smooth interaction flow
- Debug overlay showing current state and progress

---

## Tech Stack

- Python
- OpenCV
- MediaPipe
- NumPy


---

## How It Works

1. Webcam frames are captured using OpenCV  
2. MediaPipe detects hand landmarks in real time  
3. Gesture detection evaluates:
   - Distance and alignment → charging pose  
   - Z-axis movement and separation change → firing gesture  
4. A state machine manages transitions:
   - IDLE → CHARGING → CHARGED → FIRING  
5. Renderer overlays visual effects using:
   - Alpha blending  
   - Gaussian blur  
   - Layered drawing techniques  
6. Output is displayed in real time  

---

## Installation

Clone the repository:

bash
git clone https://github.com/your-username/kamehameha-gesture-system.git
cd kamehameha_project

Create Virtual Environment:
python -m venv venv
venv\Scripts\activate

Install dependencies:
pip install -r kamehameha/requirements.txt

python kamehameha/main.py

Controls
-Hold both hands together → Start charging
-Hold for ~1–2 seconds → Build energy
-Perform one of the following to fire:
-Push hands forward toward camera
-Quickly spread hands sideways
-Press Q or ESC to exit

Future Improvements
Voice trigger ("Kamehameha")
Particle-based explosion effects
Full-body pose tracking
GPU acceleration for performance
Web or mobile deployment

Author
Shivam Gupta
