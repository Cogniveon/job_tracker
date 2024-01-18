import json
import os
import sys
import time
from datetime import datetime

import camera_preview
import cv2
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QGuiApplication, QImage
from PySide6.QtQml import QmlElement, QQmlApplicationEngine
from sample_tracker import SampleTracker
from utils import opencv_to_qimage, qimage_to_opencv


class Backend(QObject):
    newPreview = Signal(QImage, arguments=["preview"])

    def __init__(self):
        super().__init__()
        # Initialize camera and YOLOv8 model
        self._image = QImage()
        self.sampleTracker = SampleTracker()

    @Slot(QImage)
    def updateImage(self, image):
        self._image = image

    @Slot(int, int)
    def startDetection(self, user, room):
        print(f"User: {user} Room: {room}")
        image = qimage_to_opencv(self._image)
        labels = self.sampleTracker.run_inference(image)

        if not os.path.exists("storage/"):
            os.mkdir("storage")

        dt = datetime.now()
        timestamp = datetime.timestamp(dt)

        output_path = f"storage/{timestamp}-{0}-{1}"
        os.mkdir(output_path)

        for i, label in enumerate(labels):
            print(label)
            with open(os.path.join(output_path, f"{i}.json"), "w") as f:
                f.write(json.dumps(label))

        preview = self.sampleTracker.annotate_labels(image, labels)

        cv2.imwrite("t.jpg", preview)

        self.newPreview.emit(opencv_to_qimage(preview))


def main():
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    backend = Backend()
    engine.rootContext().setContextProperty("backend", backend)
    engine.setInitialProperties(
        {"users": ["Rohit", "Anand"], "rooms": ["Room 1", "Room 2", "Room 3"]}
    )

    engine.load("Main.qml")
    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
