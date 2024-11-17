#!/usr/bin/env bash
rm -rf build dist
pyinstaller --onefile \
  --add-data "$VIRTUAL_ENV/lib/python3.9/site-packages/mediapipe/modules/pose_landmark/pose_landmark_full.tflite:mediapipe/modules/pose_landmark" \
  --add-data "$VIRTUAL_ENV/lib/python3.9/site-packages/mediapipe/modules/pose_detection/pose_detection.tflite:mediapipe/modules/pose_detection" \
  --add-data "$VIRTUAL_ENV/lib/python3.9/site-packages/mediapipe/modules/pose_landmark/pose_landmark_cpu.binarypb:mediapipe/modules/pose_landmark" \
  --clean \
  --hidden-import="mediapipe.python.solutions.pose" main.py

mkdir -p builds
cp dist/main builds/macos-vision-interface
