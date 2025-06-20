import cv2
import time

def record_video(duration_seconds=10, output_filename="recording.avi"):
    """
    Accesses the default camera, records video for a specified duration,
    and saves it to a file.

    Args:
        duration_seconds (int): The duration of the recording in seconds.
        output_filename (str): The name of the output video file.
    """
    # --- 1. SETUP ---
    
    # Select the default camera (usually index 0)
    # If you have multiple cameras, you might need to change this to 1, 2, etc.
    cap = cv2.VideoCapture(0)

    # Check if the camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    # Get video properties (width, height, frames per second) from the camera
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # If FPS is not available from the camera, default to 20
    if fps == 0:
        fps = 20.0
        print("Warning: Could not get FPS from camera. Defaulting to 20 FPS.")

    # Define the codec and create a VideoWriter object
    # The 'XVID' codec is a good choice for AVI files.
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_filename, fourcc, fps, (frame_width, frame_height))

    print(f"Recording for {duration_seconds} seconds... Press 'q' to stop early.")
    print(f"Video will be saved as '{output_filename}'")
    
    start_time = time.time()

    # --- 2. RECORDING LOOP ---
    
    while (time.time() - start_time) < duration_seconds:
        # Capture frame-by-frame
        ret, frame = cap.read()

        if ret:
            # Write the captured frame to the output file
            out.write(frame)

            # Display the resulting frame in a window
            cv2.imshow('Recording... (Press "q" to stop)', frame)

            # Check if the 'q' key was pressed to quit the recording early
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Recording stopped by user.")
                break
        else:
            print("Error: Failed to capture frame.")
            break

    # --- 3. CLEANUP ---

    print("Recording complete.")
    
    # Release the video capture and video write objects
    cap.release()
    out.release()

    # Close all OpenCV windows
    cv2.destroyAllWindows()


if __name__ == '__main__':
    # Run the recording function
    record_video(duration_seconds=10, output_filename="recording.avi")
