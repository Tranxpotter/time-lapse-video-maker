import cv2
import os

def extract_frames_from_video(video_file, output_folder):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Capture the video
    video_capture = cv2.VideoCapture(video_file)

    frame_count = 0

    while True:
        # Read a frame from the video
        success, frame = video_capture.read()
        
        # If the frame was not grabbed, we have reached the end of the video
        if not success:
            break

        # Save the frame as an image
        frame_filename = os.path.join(output_folder, f'frame_{frame_count:04d}.jpg')
        cv2.imwrite(frame_filename, frame)
        frame_count += 1

    # Release the video capture object
    video_capture.release()
    print(f'Extracted {frame_count} frames to {output_folder}')

# Example usage
video_file = '2025-01-18 15-36-22.mp4'  # Change this to your video file path
output_folder = 'output_frames'          # Desired output folder for images
extract_frames_from_video(video_file, output_folder)