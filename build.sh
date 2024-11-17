#!/usr/bin/env bash
pyinstaller --onefile \
  --add-data "./.venv/lib/python3.9/site-packages/mediapipe/modules/pose_landmark/pose_landmark_full.tflite:mediapipe/modules/pose_landmark" \
  --add-data "./.venv/lib/python3.9/site-packages/mediapipe/modules/pose_detection/pose_detection.tflite:mediapipe/modules/pose_detection" \
  --add-data "./.venv/lib/python3.9/site-packages/mediapipe/modules/pose_landmark/pose_landmark_cpu.binarypb:mediapipe/modules/pose_landmark" \
  --hidden-import="mediapipe.python.solutions.pose" main.py
