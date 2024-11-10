import numpy as np
import cv2
from cv2 import aruco
import multiprocessing
from EdeskModule.canvaslib import Canvas
from EdeskModule.cameralib import Camera
from EdeskModule.detectorlib import YoloDetector,ArucoDetector
from EdeskModule.contentlib import ContentManager

from multiprocessing import RawArray,Process
from time import perf_counter

#Parameter for Realsense
#USB3.1のときは1280x720まで可能，USB抜き差しでうまく3.1で認識させること または640x480
width_realsense=1280
height_realsense=720
fps_realsense=30



padding_projector=80
def setup():
    canvas=Canvas()
    camera=Camera(width_realsense,height_realsense,fps_realsense)
    # yoloDetector=YoloDetector()
    # arucoDetector=ArucoDetector()
    # contentManager=ContentManager()
    #camera.connect()
    while True:
        camera.update()

def update():
    # camera.update()
    pass
if __name__ == "__main__":
    setup()
    while True:
        update()
    pass