#detect周りの処理をこっちに書く
from multiprocessing import Manager,Process
import cv2
from cv2 import aruco
from ultralytics import YOLO
import numpy as np
from copy import deepcopy
from EdeskModule.sharedObject import MyProcess,Constants
class Detector(MyProcess):
    c=None
    def __init__(self):
        self.c=Constants()
        pass
    def setup(self):
        pass
    def update(self):
        pass


class ArucoDetector(Detector):
    dict_aruco=None
    detector=None
    def setup(self):
        #aruco setup
        self.dict_aruco = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
        self.detector=aruco.ArucoDetector(self.dict_aruco)
        # print("Aruco Setup Done!!!")
        pass
    def update(self):
        # detect AR markers
        corners, ids, rejectedImgPoints = self.detector.detectMarkers(self.cameraColorMat)
        self.arucoResult[0]=deepcopy(corners)
        self.arucoResult[1]=deepcopy(ids)
        if self.c.DEBUG:
            # self.colorMat[100:200,100:150,0]=255
            mat=np.copy(self.cameraColorMat)
            aruco.drawDetectedMarkers(mat,corners,ids)
            cv2.imshow("Aruco",mat)
            cv2.waitKey(1)
            # print("Aruco Update Done!!!",corners)
        pass
    pass
class YoloDetector(Detector):
    pass

