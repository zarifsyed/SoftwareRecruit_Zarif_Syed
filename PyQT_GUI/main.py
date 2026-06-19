import sys
import cv2
import time
from datetime import datetime
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
two duplicated camera feeds in a 1x2 grid layout. The webcam is opened using OpenCV, and each captured frame is copied into all feed panels.

PyQT6 was used for the GUI
OpenCV was used to capture the webcam frames.
QThread was used so the video capture loop does not freeze the GUI when starting/stopping feeds.

"""

class VideoFunction(QThread):
    """
    Background worker thread which is responsible for reading the frames from the webcam.

    The following classes uses OpenCV to open the webcam and read frames continuously.
    From there, it sends the frames to the GUI, using PyQT signals, so the main windows remains responsive while running.
    Also, a live timestamp is built into the camera feed, for any logistic purposes.
    """

    frame_signal = pyqtSignal(QImage)
    status_signal = pyqtSignal(str)
    fps_signal = pyqtSignal(float)

    def __init__(self, source=0):
        super().__init__()
        self.source = source
        self.running = False
        self.cap = None

    def run(self):
        # Open the webcam souce (source=0: default webcam)
        self.cap = cv2.VideoCapture(self.source)

        if not self.cap.isOpened():
            self.status_signal.emit("Camera is unavailable.")
            return
        
        self.status_signal.emit("Running.")

        frame_count = 0
        t_start = time.monotonic()

        while self.running:
            working, frame = self.cap.read()

            if not working:
                self.status_signal.emit("No frame was received.")
                continue
            
            # Add a timestamp overlay, integrated into each video feed.
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(frame, timestamp, (10,30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.7, (0,255,0),2,)

            #Note that OpenCV use BGR, but PyQT uses RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            h, w, channels = rgb_frame.shape
            bytes_per_line = channels * w

            #Convert the OpenCV frame into a QImage, which is needed to display on PyQT widgets.
            image = QImage(
                rgb_frame.data,
                w,
                h,
                bytes_per_line,
                QImage.Format.Format_RGB888,
            )

            #Sends a copy of the processed webcam frame to the GUI Thread (Dashboard)
            #By using copy(), it prevents any possible memory issues between threads
            self.frame_signal.emit(image.copy())
            
            # FPS Calulcation every 30 frames for a stable reading
            frame_count += 1
            if frame_count >= 30:
                time_elapsed = time.monotonic() - t_start
                self.fps_signal.emit(frame_count / time_elapsed if time_elapsed else 0)
                frame_count = 0
                t_start = time.monotonic()

            self.msleep(33)

        # When the thread is stopped, release webcam resources
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
    - FPS Counter
    
    """

    def __init__(self, feed_num, source=0):
        super().__init__()

        self.feed_num = feed_num
        self.source = source

        self.title_label = QLabel(f"Feed {feed_num}")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")

        self.fps_label = QLabel("FPS")
        self.fps_label.setStyleSheet("font-size 12px; font-weight: bold")

        self.fps_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )


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
        layout.addWidget(self.fps_label)
        

        self.setLayout(layout)


    def update_frame(self, image):
        pixmap = QPixmap.fromImage(image)

        #Scale the image, so it fits the display area
        # Original aspect ratio is also preserved
        scaled_pixmap = pixmap.scaled(
            self.video_label.width(),
            self.video_label.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.video_label.setPixmap(scaled_pixmap)

    def update_status(self, status):
        """
        Updates the status of each feed
        """
        self.status_label.setText(status)

    def update_fps(self, fps):
        """
        Responsible for updating the FPS counter for each feed
        """
        self.fps_label.setText(f"FPS: {fps:.1f}")


    def clear_feed(self):
        """
        Resets the feed displays to initial, default state
        """
        self.video_label.clear()
        self.video_label.setText("No Video")
        self.status_label.setText("Stopped")
        self.fps_label.setText("FPS")

class Dashboard(QWidget):
    """
    This is the main application window.
    
    This class creates two CameraFeed widgets in a 1x2 grid,
    and then uses a shared VideoFunction worker. After, each incoming frame is duplicated across all two feed panels.
    """
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Multi-Feed Camera GUI")
        self.resize(1100, 600)

        self.feeds = []

        main_layout = QVBoxLayout()
        grid_layout = QGridLayout()

        #Main function that creates the two feed panels. Duplicates the displays of one webcam source.
        for i in range(2):
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
        #Creates one camera worker, and the captured frames are sent to all feed panels.
        self.worker = VideoFunction(source)
        self.worker.frame_signal.connect(self.update_all_frames)
        self.worker.status_signal.connect(self.update_all_status)
        self.worker.fps_signal.connect(self.update_all_fps)

    def start_all(self):
        """
        Starts the camera worker thread, and updates all feeds.
        """
        if not self.worker.isRunning():
            self.worker.running = True
            self.worker.start()

    def stop_all(self):
        """
        Stops the camera worker thread, and clears all feeds.
        """
        if self.worker.isRunning():
            self.worker.stop()
        for feed in self.feeds:
            feed.clear_feed()

    #This function duplicates the webcam frames into each feed panel.
    def update_all_frames(self, image):
        """
        Updates every feed with the newest frame from the webcam.
        """
        for feed in self.feeds:
            feed.update_frame(image)

    def update_all_status(self, status):
        """
        Updates the status of the feeds.
        Calls update_status() to do so.
        """
        for feed in self.feeds:
            feed.update_status(status)

    def update_all_fps(self, fps):
        """
        Updates the FPS counter for each feed.
        Calls update_fps() to do so.
        """
        for feed in self.feeds:
            feed.update_fps(fps)

    def closeEvent(self, event):
        self.stop_all()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = Dashboard()
    window.show()

    sys.exit(app.exec())
