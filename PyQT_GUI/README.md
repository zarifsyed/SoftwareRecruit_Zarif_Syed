# Multi-Feed Camera GUI

Overview

The following project is a desktop application, using PyQT6, that displays two duplicated camera feeds in a 1x2 grid layout. The application uses OpenCV to enable one webcam and displays the same live video (frames) on all two feed panels.

The purpose of this design is to emulate a multi-camera dashboard using a single camera, rather than multiple.

Application Features:

 - PyQT6 GUI
 - two camera feed panels (1x2 grid layout)
 - Start and Stop feed buttons
 - Status labels for each feed
 - Frame captures from webcam using OpenCV
 - Background video thread to keep GUI responsive
 - Duplicated display of live feed on all six panels

# Design Breakdown

The program utilizes three main classes:

## VideoFunction

VideoFunction is a class that represents a background thread, which handles the webcam capture. It uses OpenCV to turn on the webcam and read its frame. Once read, it converts OpenCV's BGR format to RGB format so it can be displayed in PyQT.

Using PyQT signals, the thread sends frames to the GUI. This, in turn, prevents the GUI window from freezing when cameras are running.

## CameraFeed

CameraFeed represents a single video panel for the GUI. Each feed panel features a title label, a space to display video, and a status label. The feeds can update its frames, updates status, and can clear back to the initial "No video" state when it is stopped.

# How to Run

First, ensure that Python is installed. From that point, also ensure that PyQT and OpenCV are installed on your system.

To Install Python, use the following link and instructions:
https://www.python.org/downloads/release/pymanager-262/

Commands to Install PyQT and OpenCV:

	python  -m  pip  install  PyQt6  opencv-python

## Controls

 - Start Feeds button: Starts the webcam and displays the duplicated, live feed in all panels.
 - Stop Feeds Button: Stops the webcam and clears all panels back to initial "No Video" state.

