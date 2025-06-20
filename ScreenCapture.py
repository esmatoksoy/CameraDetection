import cv2

def capture_frame_from_video(video_path='recording.avi', output_image='face.jpg'):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Cannot open video file {video_path}")
        return

    ret, frame = cap.read()
    if ret:
        cv2.imwrite(output_image, frame)
        print(f"Frame saved as {output_image}")
    else:
        print("Error: Cannot read frame from video.")

    cap.release()

# Example usage:
if __name__ == "__main__":
    capture_frame_from_video()