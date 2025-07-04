import cv2
import numpy as np
import time
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=r"C:\Users\esma-\dev\CameraDetection\infos.env")
# Read values from environment variables
FROM_EMAIL = os.getenv("FROM_EMAIL")
PASSWORD = os.getenv("PASSWORD")  
TO_EMAIL = os.getenv("TO_EMAIL")


def record_on_motion(output_path="output.avi", threshold=30, min_motion_pixels=10000, inactivity_timeout=5.0):
 
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Cannot open camera.")
        return

    # Get frame dimensions for the video writer
    ret, frame = cap.read()
    if not ret:
        print("Error: Cannot read frame from camera.")
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

def capture_frame_from_video(video_path='output.avi', output_image='face.jpg'):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Cannot open video file {video_path}")
        return False

    ret, frame = cap.read()
    if ret:
        cv2.imwrite(output_image, frame)
        print(f"Frame saved as {output_image}")
        cap.release()
        return True
    else:
        print("Error: Cannot read frame from video.")
        cap.release()
        return False

def faceDetect():
    # Load the pre-trained Haar Cascade face detector
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Open the video file
    cap = cv2.VideoCapture(r"C:\Users\esma-\dev\CameraDetection\output.avi")

    face_found = False

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        if len(faces) > 0:
            face_found = True
            break

    cap.release()

    if face_found:
        print("Face detected in the video.")
        return True
    else:
        print("No face detected in the video.")
        return False
    
from MailPhotoSender import MailPhotoSender
def send_face_detected_email():
   
    sender = MailPhotoSender(
        from_email=FROM_EMAIL,
        password=PASSWORD,
        smtp_server="smtp.gmail.com",
        smtp_port=587
    )
    subject = "Test Email with Image"
    body = "This is a test email with an attached image."
    image_path = r"C:\Users\esma-\dev\CameraDetection\face.jpg"

    sender.send_mail_with_image(subject=subject, body=body, to_email=TO_EMAIL , image_path=image_path)
    print("Email with image sent successfully.")
            


if __name__ == "__main__":
    VIDEO_PATH = "output.avi"
    IMAGE_PATH = "face.jpg"
    
    # Start the motion detection and recording process
    video_was_recorded = record_on_motion()
    
    # If a video was successfully recorded, proceed with analysis
    if video_was_recorded:
        face_found = faceDetect()
        if face_found==True:
            # Capture a frame only if a face was found
            frame_saved = capture_frame_from_video()
            if frame_saved:
                send_face_detected_email()
                print("Face detected and email sent successfully.")