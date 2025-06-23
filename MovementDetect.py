import cv2
import numpy as np
import time
import os

def video_capture(output_path="output.avi", duration=10):
    cap = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, 20.0, (640, 480))
    start_time = time.time()
    while int(time.time() - start_time) < duration:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)
    cap.release()
    out.release()

def detect_motion(threshold=30.5, check_interval=1):
    cap = cv2.VideoCapture(0)
    ret, prev_frame = cap.read()
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    while True:
        time.sleep(check_interval)
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(prev_gray, gray)
        non_zero_count = np.count_nonzero(diff > threshold)
        if non_zero_count > 0:
            print("Motion detected! Starting recording...")
            cap.release()
            video_capture()
            break
        prev_gray = gray
    cap.release()

if __name__ == "__main__":
    # This script cannot wake the computer from sleep mode.
    # It must be running while the computer is awake.
    detect_motion()