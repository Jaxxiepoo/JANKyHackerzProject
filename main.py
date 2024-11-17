#!/usr/bin/env python3
import math

import cv2
import mediapipe as mp

import controls

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# Start video capture
cap = cv2.VideoCapture(0)  # 0 is the default camera

past_shoulder_poses = None
SHOULDER_COUNT_TO_AVERAGE = 200
shoulder_threshold = 100
shoulder_average = None
shoulder_pos_i = 0

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

left = False
right = False
up = False
down = False

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
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        arm_positions = {
            'left_arm': [],
            'right_arm': []
        }
        nose_pos = results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE]
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

        cur_shoulder_y = (arm_positions['right_arm'][0]['y'] + arm_positions['left_arm'][0]['y']) / 2
        if past_shoulder_poses is None:
            shoulder_average = cur_shoulder_y
            past_shoulder_poses = [cur_shoulder_y for _ in range(SHOULDER_COUNT_TO_AVERAGE)]

        shoulder_average += cur_shoulder_y / SHOULDER_COUNT_TO_AVERAGE
        shoulder_average -= past_shoulder_poses[shoulder_pos_i] / SHOULDER_COUNT_TO_AVERAGE
        past_shoulder_poses[shoulder_pos_i] = cur_shoulder_y
        shoulder_pos_i = (shoulder_pos_i + 1) % SHOULDER_COUNT_TO_AVERAGE

        # if cur_shoulder_y < shoulder_average - 100:
        #     if not up:
        #         controls.up()
        #         up = True
        # else: up = False
        # if cur_shoulder_y < shoulder_average + 100:
        #     if not down:
        #         controls.down()
        #         down = True
        # else: down = False

        # elbows above shoulders
        def is_wrist_up(arm):
            return arm_positions[arm][0]['y'] > arm_positions[arm][1]['y']

        def is_wrist_down(arm):
            return arm_positions[arm][2]['y'] > arm_positions[arm][1]['y']

        if is_wrist_up('right_arm') and is_wrist_up('left_arm'):
            if not up:
                controls.up()
                up = True
        else: up = False

        if not up and is_wrist_down('right_arm') and is_wrist_down('left_arm'):
            if not down:
                controls.down()
                down = True
        else: down = False



        THRESHOLD = math.hypot(arm_positions['right_arm'][1]['x'] - arm_positions['right_arm'][0]['x'], arm_positions['right_arm'][1]['y'] - arm_positions['right_arm'][0]['y'])
        if arm_positions['right_arm'][2]['x'] - arm_positions['right_arm'][0]['x'] > THRESHOLD:
            if not right:
                controls.right()
                right = True
        else: right = False
        THRESHOLD = math.hypot(arm_positions['left_arm'][1]['x'] - arm_positions['left_arm'][0]['x'], arm_positions['left_arm'][1]['y'] - arm_positions['left_arm'][0]['y'])
        if arm_positions['left_arm'][2]['x'] - arm_positions['left_arm'][0]['x'] < -THRESHOLD:
            if not left:
                controls.left()
                left = True
        else: left = False

        cv2.line(frame, (0, int(shoulder_average)), (500,  int(shoulder_average)), (255, 100, 0), 2)
        cv2.line(frame, (0, int(shoulder_average + shoulder_threshold)), (500,  int(shoulder_average + shoulder_threshold)), (255, 255, 0), 2)
        cv2.line(frame, (0, int(shoulder_average - shoulder_threshold)), (500,  int(shoulder_average - shoulder_threshold)), (255, 255, 0), 2)
    else:
        print("No pose landmarks detected.")

    for i in range(0, frame.shape[1], 100):
        cv2.line(frame, (0, i), (100, i), (255, 0, 0), 2)


    # Display the frame
    cv2.imshow('Pose Tracking', frame)

    # Break loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()