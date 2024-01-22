import config
import cv2
from PySide6.QtCore import Property, QObject, Qt, QTimer, Signal, Slot
from PySide6.QtGui import QImage, QPainter
from PySide6.QtQml import QmlElement, QmlSingleton
from PySide6.QtQuick import QQuickPaintedItem
from utils import opencv_to_qimage, qimage_to_opencv

QML_IMPORT_NAME = "camera_preview"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class CameraPreview(QQuickPaintedItem):
    newImage = Signal(QImage, arguments=["newImage"])
    isPlaying = Signal(bool, arguments=["isPlaying"])

    def __init__(self, parent=None):
        super(CameraPreview, self).__init__(parent)

        self._image = QImage()

        self._selectedCapture = config.CAMERA_DEVICE_ID
        self.cap = cv2.VideoCapture(self._selectedCapture)

        # Timer for updating the content
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateFrame)
        # Update every 30 ms
        self.timer.start(30)

    def paint(self, painter):
        if not self._image.isNull():
            painter.drawImage(0, 0, self._image)

    def updateFrame(self):
        if not self.cap.isOpened():
            return

        ret, frame = self.cap.read()
        if ret:
            convert_to_Qt_format = opencv_to_qimage(frame)
            convert_to_Qt_format = opencv_to_qimage(
                cv2.imread("../model_src/dataset/extracted_frames/images/frame_49.jpg")
            )
            self._image = convert_to_Qt_format.scaled(
                640, 480, aspectMode=Qt.AspectRatioMode.IgnoreAspectRatio
            )
            self.newImage.emit(self._image)
            # Triggers the paint() method
            self.update()

    @Slot(QImage)
    def updatePreview(self, preview):
        self._image = preview
        self.update()

    @Slot()
    def pause(self):
        self.isPlaying.emit(False)
        self.timer.stop()
        self.cap.release()

    @Slot()
    def resume(self):
        self.isPlaying.emit(True)
        self.cap = cv2.VideoCapture(self._selectedCapture)

        # Update every 30 ms
        self.timer.start(30)
