#これが新しいメイン
#python3 Start.pyで実行
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

class Main:
    #Parameter for Realsense
    #USB3.1のときは1280x720まで可能，USB抜き差しでうまく3.1で認識させること または640x480
    width_realsense=1280
    height_realsense=720
    fps_realsense=30

    padding_projector=80

    def __init__(self):
        self.setup()
        pass
    def setup(self):
        self.canvas=Canvas()
        self.camera=Camera(self.width_realsense,self.height_realsense,self.fps_realsense)
        pass
    def update(self):
        self.camera.update()
        pass
    pass


def setup():
    # yoloDetector=YoloDetector()
    # arucoDetector=ArucoDetector()
    # contentManager=ContentManager()
    #camera.connect()
    # while True:
    pass
        

def update():
    # camera.update()
    pass
if __name__ == "__main__":
    main=Main()

    while True:
        main.update()
    pass
