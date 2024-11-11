#detect周りの処理をこっちに書く
from multiprocessing import Manager,Process
import cv2
from cv2 import aruco
from ultralytics import YOLO
import numpy as np
from copy import deepcopy
class Detector:
    DEBUG=True
    result=None
    colorMat=None
    depthMat=None
    width=None
    height=None
    def __init__(self,width,height):
        self.width=width
        self.height=height
        pass
    def setup(self):
        pass
    def update(self):
        pass
    #各detect結果の配列を返す
    def process(self,result,colorBuffer,depthBuffer):
        self.result=result
        cvec=np.ctypeslib.as_array(colorBuffer)
        self.colorMat=cvec.reshape(self.height,self.width,3)
        dvec=np.ctypeslib.as_array(depthBuffer)
        self.depthMat=dvec.reshape(self.height,self.width,3)
        
        self.setup()
        while True:
            self.update()
        pass
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
        corners, ids, rejectedImgPoints = self.detector.detectMarkers(self.colorMat)
        self.result[0]=deepcopy(corners)
        self.result[1]=deepcopy(ids)
        if self.DEBUG:
            # self.colorMat[100:200,100:150,0]=255
            mat=np.copy(self.colorMat)
            aruco.drawDetectedMarkers(mat,corners,ids)
            cv2.imshow("Aruco",mat)
            cv2.waitKey(1)
            # print("Aruco Update Done!!!",corners)
        pass
    pass
class YoloDetector(Detector):
    pass

#こいつがさらにAruco用とYolo用のProcessを建てる
class DetectorsManager:
    
    def setup(self):
        pass
    def getResult(self):
        return (self.arucoResult,self.yoloResult)
    pass