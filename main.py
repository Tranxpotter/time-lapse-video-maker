import cv2
import os
import time

def create_video_from_images(image_folder, output_video_file, fps=30):
    # Get list of all images in the folder
    images = os.listdir(image_folder)
    
    # Sort images by name
    images.sort()

    # Read the first image to get the width and height
    first_image = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, layers = first_image.shape

    # Define the codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # or use 'XVID' for .avi
    video = cv2.VideoWriter(output_video_file, fourcc, fps, (1000, 1000))

    # Loop through all images and add them to the video
    for image in images:
        img_path = os.path.join(image_folder, image)
        frame = cv2.imread(img_path)
        frame2 = cv2.resize(frame, (1000, 1000))
        video.write(frame2)  # Write the frame to the video

    # Release the video writer and close windows
    video.release()
    cv2.destroyAllWindows()
    print(f'Video {output_video_file} created successfully!')
    print("Time taken:", time.time() - start)

start = time.time()
# Example usage
image_folder = '20250309jpg'  # Change this to your image folder path
output_video_file = 'output_video.mp4'  # Desired output video file name
create_video_from_images(image_folder, output_video_file)