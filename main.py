#!/usr/bin/env python3
from random import random

import cv2
import mediapipe as mp
from fontTools.ttLib.tables.grUtils import entries

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# Start video capture
cap = cv2.VideoCapture(0)  # 0 is the default camera

arm_landmarks = {
    'left_arm': [
        mp_pose.PoseLandmark.LEFT_SHOULDER,
        mp_pose.PoseLandmark.LEFT_ELBOW,
        mp_pose.PoseLandmark.LEFT_WRIST
    ],
    'right_arm': [
        mp_pose.PoseLandmark.RIGHT_SHOULDER,
        mp_pose.PoseLandmark.RIGHT_ELBOW,
        mp_pose.PoseLandmark.RIGHT_WRIST
    ]
}

if not cap.isOpened():
    print("Error: Could not open video capture.")
    exit()

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        break

    frame = cv2.flip(frame, 1)
    # Convert the frame to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame and detect poses
    results = pose.process(frame_rgb)

    # Draw pose landmarks
    if results.pose_landmarks:
        arm_positions = {
            'left_arm': [],
            'right_arm': []
        }
        if results.pose_landmarks:
            for side in ['left_arm', 'right_arm']:
                for landmark in arm_landmarks[side]:
                    point = results.pose_landmarks.landmark[landmark]
                    # Convert normalized coordinates to pixel coordinates
                    x = int(point.x * frame.shape[1])
                    y = int(point.y * frame.shape[0])
                    z = point.z
                    visibility = point.visibility

                    arm_positions[side].append({
                        'x': x,
                        'y': y,
                        'z': z,
                        'visibility': visibility,
                        'landmark': landmark.name
                    })

        print(arm_positions)
        for _, arm in arm_positions.items():
            for i, point in enumerate(arm):
                p = (int(arm[i]['x']), int(arm[i]['y']))
                cv2.circle(frame, p, 5, (0, 255, 0), -1)
    else:
        print("No pose landmarks detected.")

    # Display the frame
    cv2.imshow('Pose Tracking', frame)

    # Break loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()