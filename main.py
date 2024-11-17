#!/usr/bin/env python3
import math
import time

import tkinter
from tkinter import font
import webbrowser

import cv2
import mediapipe as mp

import controls

def toggle_running():
    global running
    running = not running

def quit_app():
    cv2.destroyAllWindows()
    root.destroy()


root = tkinter.Tk()
root.title("Control window")

button_font = font.Font()

def launcher(url):
    return lambda: webbrowser.open(url)

games = {
    "Run 3": "https://run3free.github.io/",
    "Subway Surfers": "https://poki.com/en/g/subway-surfers",
    "Temple Run": "https://poki.com/en/g/temple-run-2",
}

for game, url in games.items():
    button = tkinter.Button(root, text=game, command=launcher(url), font=button_font)
    button.pack()

quit_button = tkinter.Button(root, text="Quit", command=quit_app, font=button_font)
quit_button.pack()

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# Start video capture
while True:
    cap = cv2.VideoCapture(0)  # 0 is the default camera
    if cap.isOpened():
        break
    time.sleep(1)

arm_landmarks = {
    'left_arm': [
        mp_pose.PoseLandmark.RIGHT_SHOULDER,
        mp_pose.PoseLandmark.RIGHT_ELBOW,
        mp_pose.PoseLandmark.RIGHT_WRIST
    ],
    'right_arm': [
        mp_pose.PoseLandmark.LEFT_SHOULDER,
        mp_pose.PoseLandmark.LEFT_ELBOW,
        mp_pose.PoseLandmark.LEFT_WRIST
    ]
}

if not cap.isOpened():
    print("Error: Could not open video capture.")
    exit()

def p2p(point) -> tuple:
    return int(point['x']), int(point['y'])

def handle_frame(frame, controls):
    # Convert the frame to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame and detect poses
    results = pose.process(frame_rgb)

    # Draw pose landmarks
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        arm_positions = {
            'left_arm': [],
            'right_arm': []
        }
        for side in arm_positions:
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

        for _, arm in arm_positions.items():
            for i, point in enumerate(arm):
                p = (int(arm[i]['x']), int(arm[i]['y']))
                cv2.circle(frame, p, max(int(20*point["z"] + 20), 1), (0, 255, 255), -1)
                if i != len(arm)-1:
                    cv2.line(frame, p2p(point), p2p(arm[i + 1]), (0, 255, 0), 3)

        # elbows above shoulders
        def is_wrist_up(arm):
            return arm_positions[arm][0]['y'] > arm_positions[arm][1]['y']

        def is_wrist_down(arm):
            return arm_positions[arm][2]['y'] > arm_positions[arm][1]['y']

        if is_wrist_up('right_arm') and is_wrist_up('left_arm'):
            controls.press("up")
        else: controls.release("up")

        if not controls.dict["up"] and is_wrist_down('right_arm') and is_wrist_down('left_arm'):
            controls.press("down")
        else: controls.release("down")

        THRESHOLD = math.hypot(arm_positions['right_arm'][1]['x'] - arm_positions['right_arm'][0]['x'], arm_positions['right_arm'][1]['y'] - arm_positions['right_arm'][0]['y'])
        if arm_positions['right_arm'][2]['x'] - arm_positions['right_arm'][0]['x'] > THRESHOLD:
            controls.press("right")
        else: controls.release("right")
        THRESHOLD = math.hypot(arm_positions['left_arm'][1]['x'] - arm_positions['left_arm'][0]['x'], arm_positions['left_arm'][1]['y'] - arm_positions['left_arm'][0]['y'])
        if arm_positions['left_arm'][2]['x'] - arm_positions['left_arm'][0]['x'] < -THRESHOLD:
            controls.press("left")
        else: controls.release("left")

        if arm_positions['right_arm'][2]['x'] < arm_positions['left_arm'][2]['x']:
            controls.press("space")
        else: controls.release("space")

    else:
        print("No pose landmarks detected.")




controls1 = controls.Controls()

def main_loop():
    if not cap.isOpened(): return
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        return quit_app()

    frame = cv2.flip(frame, 1)
    handle_frame(frame, controls1)
    # Display the frame
    cv2.imshow('Pose Tracking', frame)

    # Break loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        return quit_app()

    root.after(10, main_loop)

# Release resources
main_loop()
root.mainloop()
cap.release()
cv2.destroyAllWindows()