import sys
import time

import camera_preview
import cv2
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QGuiApplication, QImage
from PySide6.QtQml import QmlElement, QQmlApplicationEngine
from ultralytics import YOLO
from utils import opencv_to_qimage, qimage_to_opencv


class Backend(QObject):
    showLoading = Signal()
    hideLoading = Signal()
    newPreview = Signal(QImage, arguments=["preview"])

    def __init__(self):
        super().__init__()
        # Initialize camera and YOLOv8 model
        self._image = QImage()
        self._model = YOLO("sample_tracker.pt")  # yolov8n.pt

    @Slot(QImage)
    def updateImage(self, image):
        self._image = image

    @Slot(int, int)
    def startDetection(self, user, room):
        self.showLoading.emit()
        print(f"User: {user} Room: {room}")

        cv_img = qimage_to_opencv(self._image)
        frame_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        results = self._model(frame_rgb)
        result_plot = results[0].plot(conf=False, probs=False, labels=True)
        result_plot = cv2.cvtColor(result_plot, cv2.COLOR_RGB2BGR)

        # cv2.rectangle(cv_img, (50, 50), (200, 200), (0, 255, 0), 2)

        self.newPreview.emit(opencv_to_qimage(result_plot))

        self.hideLoading.emit()


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
