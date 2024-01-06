import argparse
import os

import cv2


def split_frames(video_path, output_folder, skip_n_frames=1):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    video_capture = cv2.VideoCapture(video_path)

    # Get information about the video
    fps = video_capture.get(cv2.CAP_PROP_FPS)
    frame_count = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

    for frame_number in range(0, frame_count, skip_n_frames):
        # Read the frame
        ret, frame = video_capture.read()

        if not ret:
            print(f"Error reading frame {frame_number}")
            break

        # Save the frame as an image
        frame_filename = os.path.join(output_folder, f"frame2_{frame_number:06d}.png")
        cv2.imwrite(frame_filename, frame)

    # Release the video capture object
    video_capture.release()
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split an MP4 video into frames.")
    parser.add_argument("video_path", help="Path to the input MP4 video file.")
    parser.add_argument("output_folder", help="Path to the output folder for frames.")
    parser.add_argument(
        "skip_n_frames", type=int, help="Skip every n frame to capture a still."
    )
    args = parser.parse_args()

    split_frames(args.video_path, args.output_folder, args.skip_n_frames)
