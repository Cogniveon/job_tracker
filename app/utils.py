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


def nms(boxes, scores, iou_threshold):
    # Sort by score
    sorted_indices = np.argsort(scores)[::-1]

    keep_boxes = []
    while sorted_indices.size > 0:
        # Pick the last box
        box_id = sorted_indices[0]
        keep_boxes.append(box_id)

        # Compute IoU of the picked box with the rest
        ious = compute_iou(boxes[box_id, :], boxes[sorted_indices[1:], :])

        # Remove boxes with IoU over the threshold
        keep_indices = np.where(ious < iou_threshold)[0]

        # print(keep_indices.shape, sorted_indices.shape)
        sorted_indices = sorted_indices[keep_indices + 1]

    return keep_boxes


def compute_iou(box, boxes):
    # Compute xmin, ymin, xmax, ymax for both boxes
    xmin = np.maximum(box[0], boxes[:, 0])
    ymin = np.maximum(box[1], boxes[:, 1])
    xmax = np.minimum(box[2], boxes[:, 2])
    ymax = np.minimum(box[3], boxes[:, 3])

    # Compute intersection area
    intersection_area = np.maximum(0, xmax - xmin) * np.maximum(0, ymax - ymin)

    # Compute union area
    box_area = (box[2] - box[0]) * (box[3] - box[1])
    boxes_area = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
    union_area = box_area + boxes_area - intersection_area

    # Compute IoU
    iou = intersection_area / union_area

    return iou


def xywh2xyxy(x):
    # Convert bounding box (x, y, w, h) to bounding box (x1, y1, x2, y2)
    y = np.copy(x)
    y[..., 0] = x[..., 0] - x[..., 2] / 2
    y[..., 1] = x[..., 1] - x[..., 3] / 2
    y[..., 2] = x[..., 0] + x[..., 2] / 2
    y[..., 3] = x[..., 1] + x[..., 3] / 2
    return y


def rescale_boxes(boxes, input_shape, image_shape):
    # Rescale boxes to original image dimensions
    input_shape = np.array(
        [input_shape[1], input_shape[0], input_shape[1], input_shape[0]]
    )
    boxes = np.divide(boxes, input_shape, dtype=np.float32)
    boxes *= np.array([image_shape[1], image_shape[0], image_shape[1], image_shape[0]])
    return boxes
