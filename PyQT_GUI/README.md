
# Multi-Feed Camera GUI

Overview

The following project is a desktop application, using PyQT6, that displays two duplicated camera feeds in a 1x2 grid layout. The application uses OpenCV to enable one webcam and displays the same live video (frames) on all two feed panels.

The purpose of this design is to emulate a multi-camera dashboard using a single camera, rather than multiple.

* The reason as to why I used OpenCV instead of GStreamer is that I, for some reason, could not get GStreamer installed on my computer. Hence, I used OpenCV as an alternative to complete this project.

Application Features:
- PyQT6 GUI

- Two camera feed panels (1x2 grid layout)

- Start and Stop feed buttons

- Status labels for each feed

- FPS Counters for each feed

- Timestamp Overlays, integrated on each video feed

- Frame captures from webcam using OpenCV

- Background video thread to keep GUI responsive

- Duplicated display of live feed on both panels

  

# Design Breakdown

  

The program utilizes three main classes:

  

## VideoFunction

  

VideoFunction is a class that represents a background thread, which handles the webcam capture. It uses OpenCV to turn on the webcam and read its frame. Once read, it converts OpenCV's BGR format to RGB format so it can be displayed in PyQT.

  

The frames captured from the camera are sent to the GUI using PyQT signals (frame_signal), so main window remains responsive while the camera is running. The current status (status_signal) and FPS (fps_signal) are also emitted, with FPS being recalculated every 30 frames for a stable reading. Additionally, a timestamp overlay is added onto each frame being sent.

  

## CameraFeed

  

CameraFeed represents a single video panel for the GUI. Each feed panel features a title label, a space to display video, a status label, and FPS counter. A panel is able to update its displayed frame, update the status label, update its FPS reading, and when stopped, reset back to its initial "No Video" state.

  

## Dashboard

  

Dashboard is responsible for the main application window, tying in the two previous classes together to build a 1x2 grid from two CameraFeed widgets and connects the start/stop buttons.


One shared VideoFunction worker is created, regardless of the amount of panel. Its corresponding frame_signal, status_signal, and fps_signal are connected, then broadcasted to every panel. As a result, this is what causes the duplicated cameras, since it is the same frame being displayed to two panels.

  
  

# How to Run

  

First, ensure that Python is installed. From that point, also ensure that PyQT and OpenCV are installed on your system.

  

To Install Python, use the following link and instructions:

https://www.python.org/downloads/release/pymanager-262/

  

Commands to Install PyQT and OpenCV:

  

	python -m pip install PyQt6 opencv-python

  

Once installed, to run the actual program, open terminal and run:

  

	python main.py

  

A new application window will pop up, and you will then be able to run the project for yourself!

  

Note: Once start feed is clicked, there is a slight delay into pressing the button, and for the feed to then start displaying the webcam.

  

## Controls

  

- Start Feeds button: Starts the webcam and displays the duplicated, live feed in all panels.

- Stop Feeds Button: Stops the webcam and clears all panels back to initial "No Video" state.

# Limitations

 - This application only uses a single camera, and the panels duplicates the same feed. 
 - The frame rate is capped at 30 FPS by a delay fixed in the capture loop, rather than using the camera's native frame rate.
 - When a frame fails to read, the loop retries instead of aborting from the operation. This could increase CPU usage on an inconsistent camera connection.

# Possible Improvements

 - Colour code each possible camera status, such as green for running, red for stopped, and orange for errors.
 - Add the function of recording and/or taking screenshots from a feed.
 
