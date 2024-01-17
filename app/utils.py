import re
import subprocess

import cv2
import numpy as np
from PySide6.QtGui import QImage


def qimage_to_opencv(qimage: QImage):
    """Converts a QImage object to an OpenCV image"""

    # Convert QImage to format compatible with OpenCV
    qimage = qimage.convertToFormat(QImage.Format.Format_RGB888)

    width = qimage.width()
    height = qimage.height()

    # Get pointer to the data
    ptr = qimage.bits()

    # Create a numpy array with the same shape
    arr = np.array(ptr).reshape(height, width, 3)  # 3 channels (R, G, B)

    # Convert RGB to BGR format which is used by OpenCV
    opencv_image = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

    return opencv_image


def opencv_to_qimage(cv_img):
    """Converts an OpenCV image to a QImage object"""

    # Check if the image has an alpha channel
    if len(cv_img.shape) == 3 and cv_img.shape[2] == 4:
        # Convert from BGR to RGBA
        qimage = QImage(
            cv_img.data,
            cv_img.shape[1],
            cv_img.shape[0],
            cv_img.strides[0],
            QImage.Format_RGBA8888,
        )
    else:
        # Convert from BGR to RGB
        cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        qimage = QImage(
            cv_img.data,
            cv_img.shape[1],
            cv_img.shape[0],
            cv_img.strides[0],
            QImage.Format_RGB888,
        )

    # Make sure to copy the data into the QImage
    return qimage.copy()


def list_video_devices():
    device_names = []
    device_paths = []

    try:
        # Run v4l2-ctl to list device names
        output = subprocess.check_output(["v4l2-ctl", "--list-devices"], text=True)
        # Parse the output
        device_sections = output.strip().split("\n\n")
        for section in device_sections:
            lines = section.split("\n")
            if len(lines) >= 2:
                # The first line is the device name, subsequent lines contain the /dev/video* entries
                name = lines[0].strip()
                dev_files = [
                    line.strip()
                    for line in lines[1:]
                    if line.strip().startswith("/dev/video")
                ]
                for dev in dev_files:
                    device_names.append(name)
                    device_paths.append(dev)
    except Exception as e:
        print(f"An error occurred: {e}")

    return device_names, device_paths
