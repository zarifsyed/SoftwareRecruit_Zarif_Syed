import sys
import cv2
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QWidget,
    QGridLayout,
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
)

"""
Multi-Feed Camera GUI

The following program, using PyQT6, creates a desktop application that displays
six duplicated camera feeds in a 2x3 grid layout. The webcam is opened using OpenCV, and each captured frame is copied into all six feed panels.

PyQT6 was used for the GUI
OpenCV was used to capture the webcam frames.
QThread was used so the video capture loop does not freeze the GUI when starting/stopping feeds.

"""

class VideoFunction(QThread):
    """
    Background worker thread which is responsible for reading the frames from the webcam.

    The following classes uses OpenCV to open the webcam and read frames continuously.
    From there, it sends the frames to the GUI, using PyQT signals, so the main windows remains responsive while running.
    """

    frame_signal = pyqtSignal(QImage)
    status_signal = pyqtSignal(str)

    def __init__(self, source=0):
        super().__init__()
        self.source = source
        self.running = False
        self.cap = None

    def run(self):
        self.cap = cv2.VideoCapture(self.source)

        if not self.cap.isOpened():
            self.status_signal.emit("Camera is unavailable.")
            return
        
        self.status_signal.emit("Running.")

        while self.running:
            working, frame = self.cap.read()

            if not working:
                self.status_signal.emit("No frame was received.")
                continue
            
            #Note that OpenCV use BGR, but PyQT uses RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            h, w, channels = rgb_frame.shape
            bytes_per_line = channels * w

            image = QImage(
                rgb_frame.data,
                w,
                h,
                bytes_per_line,
                QImage.Format.Format_RGB888,
            )

            self.frame_signal.emit(image.copy())
            self.msleep(33)

        if self.cap is not None:
            self.cap.release()
            self.cap = None

        self.status_signal.emit("Stopped")

    def stop(self):
        self.running = False

        if self.cap is not None:
            self.cap.release()
            self.cap = None
    

class CameraFeed(QWidget):
    """
    Represents a visual camera feed panel within the GUI

    Each panels is as follows:
    - Feed title
    - Video display space 
    - Status label
    
    """

    def __init__(self, feed_num, source=0):
        super().__init__()

        self.feed_num = feed_num
        self.source = source

        self.title_label = QLabel(f"Feed {feed_num}")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")

        self.video_label = QLabel("No video")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setMinimumSize(320,320)
        self.video_label.setStyleSheet("background-color: black; color: white; border: 2px solid gray;")

        self.status_label = QLabel("Stopped")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addWidget(self.video_label)
        layout.addWidget(self.status_label)

        self.setLayout(layout)


    def update_frame(self, image):
        pixmap = QPixmap.fromImage(image)

        scaled_pixmap = pixmap.scaled(
            self.video_label.width(),
            self.video_label.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.video_label.setPixmap(scaled_pixmap)

    def update_status(self, status):
        self.status_label.setText(status)

    def clear_feed(self):
        self.video_label.clear()
        self.video_label.setText("No Video")
        self.status_label.setText("Stopped")

class Dashboard(QWidget):
    """
    This is the main application window.
    
    This class creates six CameraFeed widgets in a 2x3 grid,
    and then uses a shared VideoFunction worker. After, each incoming frame is duplicated across all six feed panels.
    """
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Multi-Feed Camera GUI")
        self.resize(1100, 750)

        self.feeds = []

        main_layout = QVBoxLayout()
        grid_layout = QGridLayout()

        #Main function that creates the six feed panels. Duplicates the displays of one webcam source.
        for i in range(6):
            feed = CameraFeed(i + 1)
            self.feeds.append(feed)

            row = i // 3
            col = i % 3

            grid_layout.addWidget(feed, row, col)


        button_layout = QHBoxLayout()

        self.start_button = QPushButton("Start Feeds")
        self.stop_button = QPushButton("Stop Feeds")

        self.start_button.clicked.connect(self.start_all)
        self.stop_button.clicked.connect(self.stop_all)

        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)

        main_layout.addLayout(grid_layout)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        source = 0
        #Creates one camera worker, and the captured frames are sent to all six feed panels.
        self.worker = VideoFunction(source)
        self.worker.frame_signal.connect(self.update_all_frames)
        self.worker.status_signal.connect(self.update_all_status)

    def start_all(self):
        if not self.worker.isRunning():
            self.worker.running = True
            self.worker.start()

    def stop_all(self):
        if self.worker.isRunning():
            self.worker.stop()
        for feed in self.feeds:
            feed.clear_feed()

    #This function duplicates the webcam frames into each feed panel.
    def update_all_frames(self, image):
        for feed in self.feeds:
            feed.update_frame(image)

    def update_all_status(self, status):
        for feed in self.feeds:
            feed.update_status(status)

    def closeEvent(self, event):
        self.stop_all()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = Dashboard()
    window.show()

    sys.exit(app.exec())
