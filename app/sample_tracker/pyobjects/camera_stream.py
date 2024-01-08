import cv2
from PySide6.QtCore import Property, QObject, Qt, QTimer, Signal, Slot
from PySide6.QtGui import QImage, QPainter
from PySide6.QtQml import QmlElement, QmlSingleton
from PySide6.QtQuick import QQuickPaintedItem

from .utils import list_video_devices, opencv_to_qimage, qimage_to_opencv

QML_IMPORT_NAME = "camera_stream"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class CameraStream(QQuickPaintedItem):
    def __init__(self, parent=None):
        super(CameraStream, self).__init__(parent)

        self._captureOptions, self._devices = list_video_devices()
        assert len(self._devices) > 0

        self._selectedCapture = self._devices[0]

        self._image = QImage()
        self.cap = cv2.VideoCapture(self._selectedCapture)

        # Timer for updating the content
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateFrame)
        # Update every 30 ms
        self.timer.start(30)

    @Property("QVariantList")
    def captureOptions(self):
        return self._captureOptions

    @Slot(int)
    def onSelectionChanged(self, index):
        self._selectedCapture = self._devices[index]

    def paint(self, painter):
        if not self._image.isNull():
            painter.drawImage(0, 0, self._image)

    def updateFrame(self):
        if not self.cap.isOpened():
            return

        ret, frame = self.cap.read()
        if ret:
            convert_to_Qt_format = opencv_to_qimage(frame)
            self._image = convert_to_Qt_format.scaled(
                640, 480, aspectMode=Qt.AspectRatioMode.KeepAspectRatio
            )
            # Triggers the paint() method
            self.update()

    @Slot()
    def startDetection(self):
        self.timer.stop()
        self.cap.release()

        cv_img = qimage_to_opencv(self._image)

    @Slot()
    def resume(self):
        self.cap = cv2.VideoCapture(self._selectedCapture)

        # Update every 30 ms
        self.timer.start(30)
