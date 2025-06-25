import os
import cv2
import time
import platform
import numpy as np
from dotenv import load_dotenv
import threading
import ctypes
import subprocess
import sys

# 1. Find the user's home directory (e.g., C:\Users\Username)
user_home = os.path.expanduser('~')

# 2. Directly target the "Documents" folder to create the application directory path
APP_DIR = os.path.join(user_home, 'Documents', 'CameraDetection')

# 3. Check if the application directory exists, create it if not.
#    exist_ok=True prevents an error if the folder already exists.
try:
    os.makedirs(APP_DIR, exist_ok=True)
    print(f"Application working directory: {APP_DIR}")
except OSError as e:
    # If the "Documents" folder cannot be found or there is a permission issue,
    # create a fallback plan to prevent the program from crashing.
    # Creates a 'data' folder next to the .exe.
    print(f"ERROR: Could not access the 'Documents' folder ({e}). Data will be saved next to the program.")
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
    APP_DIR = os.path.join(application_path, 'CameraDetectionData')
    os.makedirs(APP_DIR, exist_ok=True)

VIDEO_PATH = os.path.join(APP_DIR, "recording.avi")
IMAGE_PATH = os.path.join(APP_DIR, "face.jpg")

os.makedirs(APP_DIR, exist_ok=True)

# Determine the main directory where the program is running
# If running as an .exe, get the folder where the .exe is located.
# If running as a .py, get the folder where the .py file is located.
if getattr(sys, 'frozen', False):
    # When packaged as .exe
    application_path = os.path.dirname(sys.executable)
else:
    # When running as a normal .py script
    application_path = os.path.dirname(os.path.abspath(__file__))

# Create the full path to the .env file
env_path = os.path.join(application_path, 'infos.env')

# Check if the .env file exists (optional but recommended)
if os.path.exists(env_path):
    print(f"Loading .env file from: {env_path}")
    load_dotenv(dotenv_path=env_path)
else:
    print(f"Error: infos.env file not found at {env_path}")
    # You can stop the program here or continue with default settings
    # For example: sys.exit("Configuration file infos.env not found!")
# This code for finding the .env file should already be in your file
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

# --- CHANGE 1: Video Recording Path ---
# OLD (probably):
# video_kayit_yolu = "recording.avi"
# NEW and CORRECT:
video_kayit_yolu = os.path.join(application_path, "recording.avi")
# ... and use this path in cv2.VideoWriter

# --- CHANGE 2: Face Image Save Path ---
# OLD (probably):
# resim_kayit_yolu = "face.jpg"
# NEW and CORRECT:
face_jpg_yolu = os.path.join(application_path, "face.jpg")
# ... and use this path in cv2.imwrite
# cv2.imwrite(face_jpg_yolu, face_frame)




# Read values from environment variables
FROM_EMAIL = os.getenv("FROM_EMAIL")
PASSWORD = os.getenv("PASSWORD")  
TO_EMAIL = os.getenv("TO_EMAIL")

if not all([FROM_EMAIL, PASSWORD, TO_EMAIL]):
    raise ValueError("Missing one or more required environment variables: FROM_EMAIL, PASSWORD, TO_EMAIL. Please check your infos.env file.")

# ---- Motion Detection ----
def record_on_motion(output_path="output.avi", threshold=20, min_motion_pixels=5000, inactivity_timeout=5.0):
 
    cap = cv2.VideoCapture(0)
    # Check if the camera opened successfully
    if not cap.isOpened():
        print("Error: Cannot open camera.")
        return

    # Try to get frame dimensions for the video writer, retrying if necessary
    max_retries = 10
    for _ in range(max_retries):
        ret, frame = cap.read()
        if ret:
            break
        time.sleep(0.2)  # Wait a bit before retrying
    if not ret:
        print("Error: Cannot read frame from camera after several attempts.")
        cap.release()
        return
    height, width, _ = frame.shape

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = None
    is_recording = False
    last_motion_time = None

    prev_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    prev_gray = cv2.GaussianBlur(prev_gray, (21, 21), 0) # Apply blur to reduce noise

    print("Ready to detect motion. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        # Compute the difference between the current and previous frame
        frame_delta = cv2.absdiff(prev_gray, gray)
        thresh = cv2.threshold(frame_delta, threshold, 255, cv2.THRESH_BINARY)[1]
        
        # Count the number of white pixels (indicating change)
        motion_pixel_count = np.count_nonzero(thresh)

        motion_detected = motion_pixel_count > min_motion_pixels

        if motion_detected:
            if not is_recording:
                # Start recording when motion is first detected
                print("Motion detected! Starting recording...")
                is_recording = True
                out = cv2.VideoWriter(output_path, fourcc, 20.0, (width, height))
            
            last_motion_time = time.time()

        if is_recording:
            # Write the frame to the file while recording
            out.write(frame)

            # Check if motion has stopped for the timeout duration
            if time.time() - last_motion_time > inactivity_timeout:
                print(f"Motion stopped. Finishing recording after {inactivity_timeout} seconds of inactivity.")
                break # Exit the loop to save the video

        prev_gray = gray
    # Cleanup
    if is_recording:
        out.release()
    cap.release()
    cv2.destroyAllWindows()
    print(f"Video saved to {output_path}" if is_recording else "No motion was recorded.")
    return is_recording # Return whether a video was actually created

def capture_frame_from_video(video_path='recording.avi', output_image='face.jpg'):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Cannot open video file {video_path}")
        return False

    ret, frame = cap.read()
    if ret:
        cv2.imwrite(face_jpg_yolu, frame)
        print(f"Frame saved as {output_image}")
        cap.release()
        return True
    else:
        print("Error: Cannot read frame from video.")
        cap.release()
        return False

# ---- Face Detection ----
def faceDetect(video_path=VIDEO_PATH):
    cap = cv2.VideoCapture(video_path)
    face_found = False
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5)
        if len(faces) > 0:
            face_found = True
            break
    cap.release()
    return face_found

# ---- Email ----
from MailPhotoSender import MailPhotoSender

def send_face_detected_email(image_path=face_jpg_yolu):
   
    sender = MailPhotoSender(
        from_email=FROM_EMAIL,
        password=PASSWORD,
        smtp_server="smtp.gmail.com",
        smtp_port=587
    )
    subject = "Test Email with Image"
    body = "This is a test email with an attached image."
    #image_path = r"C:\Users\esma-\dev\CameraDetection\face.jpg"

    sender.send_mail_with_image(subject=subject, body=body, to_email=TO_EMAIL , image_path=image_path)

# ---- Cross-platform Autostart Setup ----
def setup_autostart():
    system = platform.system()
    script_path = os.path.abspath(__file__)

    if system == "Windows":
        try:
            import winreg

            reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(reg_key, "CameraDetection", 0, winreg.REG_SZ, f'"{script_path}"')
            winreg.CloseKey(reg_key)
            print("Autostart added to Windows Registry.")
        except Exception as e:
            print(f"Windows autostart error: {e}")

    elif system == "Darwin":
        plist_content = f"""
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" 
    "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.cameradetect</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>{script_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
"""
        plist_path = os.path.expanduser("~/Library/LaunchAgents/com.user.cameradetect.plist")
        with open(plist_path, "w") as f:
            f.write(plist_content)
        print("Autostart plist added for macOS.")

    elif system == "Linux":
        desktop_entry = f"""
[Desktop Entry]
Type=Application
Exec=python3 {script_path}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=CameraDetection
Comment=Start on login
"""
        autostart_dir = os.path.expanduser("~/.config/autostart")
        os.makedirs(autostart_dir, exist_ok=True)
        desktop_file = os.path.join(autostart_dir, "cameradetect.desktop")
        with open(desktop_file, "w") as f:
            f.write(desktop_entry)
        print("Autostart added for Linux.")

# ---- Main ----

def is_screen_locked():
    system = platform.system()
    if system == "Windows":
        try:
            user32 = ctypes.windll.User32
            # 0 = unlocked, 1 = locked
            return user32.GetForegroundWindow() == 0
        except Exception:
            return False
    elif system == "Darwin":
        # macOS: check for loginwindow process in front
        try:
            front_app = subprocess.check_output(
                ["osascript", "-e", 'tell application "System Events" to get name of first process whose frontmost is true']
            ).decode().strip()
            return front_app == "loginwindow"
        except Exception:
            return False
    elif system == "Linux":
        # Linux: check for screensaver/locker process
        try:
            output = subprocess.check_output("loginctl show-session $(loginctl | awk '/tty/ {print $1}') -p LockedHint", shell=True)
            return b"yes" in output
        except Exception:
            return False
    return False

if __name__ == "__main__":
    setup_autostart()  # Adds auto-run on startup (first run only)
    system = platform.system()
    print(f"Detected OS: {system}")

    def main_loop():
        camera_active = False
        while True:
            if is_screen_locked():
                if not camera_active:
                    print("Screen locked. Starting motion detection.")
                    time.sleep(5)  # Wait a bit before starting detection
                    # Start motion detection and face capture
                    camera_active = True
                    if record_on_motion(VIDEO_PATH):
                        if faceDetect(VIDEO_PATH):
                            if capture_frame_from_video(VIDEO_PATH, IMAGE_PATH):
                                send_face_detected_email()
                # Stay in this state until unlocked
                while is_screen_locked():
                    time.sleep(0.1)
                print("Screen unlocked. Waiting for next lock event.")
                camera_active = False
            time.sleep(0.5)  # Poll for lock status

    t = threading.Thread(target=main_loop, daemon=True)
    t.start()
    # Keep main thread alive
    while True:
        time.sleep(5)