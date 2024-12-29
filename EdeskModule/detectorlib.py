#detect周りの処理をこっちに書く
from multiprocessing import Manager,Process
import cv2
from cv2 import aruco
from ultralytics import YOLO
import numpy as np
from copy import deepcopy
from EdeskModule.sharedObject import MyProcess,Constants
import time
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
            cv2.imwrite("Aruco.png",mat)
            cv2.waitKey(1)
            # print("Aruco Update Done!!!",corners)
        pass
    pass
# class YoloDetector(Detector):
#     model_color=None
#     nodel_depth=None
#     color_on=True
#     depth_on=False
#     def setup(self):
#         self.model_color=YOLO("./models/best_color.pt")
#         self.model_depth=YOLO("./models/best_depth.pt")
#         print("YOLO setup")
#         pass
#     def update(self):
#         print("Yolo update")
#         if self.color_on:
#             print("Yolo 1")
#             color_smallMat=cv2.resize(self.cameraColorMat,None,fx=0.5,fy=0.5)
#             print("Yolo 2")
#             result_color=self.model_color.predict(color_smallMat)
#             print("Yolo 3")
#             result_color_boxes=result_color[0].boxes.numpy()
#             print("Yolo 4")
#             self.yoloResult[0]=deepcopy(result_color_boxes)
            
#             print("in YOLO",self.yoloResult)
#             pass
#         if self.depth_on:
#             depth_gray = (self.cameraDepthMat/256).astype('uint8')
#             depth_gray=cv2.cvtColor(depth_gray,cv2.COLOR_GRAY2RGB)
#             depth_gray_small=cv2.resize(depth_gray,None,fx=0.5,fy=0.5)
#             result_depth=self.model_depth(depth_gray_small)
#             result_depth_boxes=result_depth[0].boxes.numpy()
#             self.yoloResult[1]=deepcopy(result_depth_boxes)
#             pass

#         pass
#     pass

def yoloColorProcessFunction(cameraColorBuffer,yoloResult:list):
    c=Constants()
    model_color=YOLO("./models/best_8n.pt")
    color_on=True
    cvec=np.ctypeslib.as_array(cameraColorBuffer)
    cameraColorMat=cvec.reshape(c.camera_height,c.camera_width,3)

    while True:
        if yoloResult[2] is False:
            time.sleep(1)
            continue
        color_smallMat=cv2.resize(cameraColorMat,None,fx=0.5,fy=0.5)
        result_color=model_color(color_smallMat)
        result_color_boxes=result_color[0].boxes.numpy()
        yoloResult[0]=deepcopy(result_color_boxes)        
        pass
    pass