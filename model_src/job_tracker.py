import os
import random
import time

import cv2
import numpy as np

# import sort
import ultralytics

ultralytics.checks()

from ultralytics import YOLO


class YOLOv8_Detector:
    """
    Base class to be used for implementing various object detectors using YOLOv8
    """

    def __init__(
        self, model_file="yolov8n.pt", classes=None, conf=0.25, iou=0.45
    ) -> None:
        self.model = YOLO(model_file)
