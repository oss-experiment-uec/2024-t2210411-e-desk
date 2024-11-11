#これが新しいメイン
#python3 Start.pyで実行
import numpy as np
import cv2
from cv2 import aruco
import multiprocessing
from EdeskModule.canvaslib import Canvas
from EdeskModule.cameralib import Camera,RealSense,NormalCamera
from EdeskModule.detectorlib import YoloDetector,ArucoDetector
from EdeskModule.contentlib import ContentManager

from multiprocessing import RawArray,Process
from time import perf_counter
import ctypes

class Main:
    #Parameter for Realsense
    #USB3.1のときは1280x720まで可能，USB抜き差しでうまく3.1で認識させること または640x480
    realsense_width=1280
    realsense_height=720
    realsense_fps=30

    #Parameter for Canvas
    projector_padding=80
    projector_width=1920
    projector_height=1000
    canvas_width=projector_width-projector_padding*2
    canvas_height=projector_height-projector_padding*2

    #1d-Array(ctype),こいつが共有メモリ 
    cameraColorBuffer=None
    cameraDepthBuffer=None
    projectingBuffer=None
    canvasBuffer=None
    #ctypeだとOpenCVで扱いにくいのでndarrayに変更．ただし同じデータを指すポインタになっているはず
    cameraColorMat=None
    cameraDepthMat=None
    projectingMat=None
    canvasMat=None

    camera=None
    canvas=None
    contentManager=None
    def __init__(self):
        self.setup()
        pass
    def initCamera(self):
        self.camera=NormalCamera(self.realsense_width,self.realsense_height,self.realsense_fps)
        # self.camera=RealSense(self.realsense_width,self.realsense_height,self.realsense_fps)
        self.cameraBufferLength=self.realsense_width*self.realsense_height*3
        
        #Camera用Bufferの作成
        cmat=np.zeros((self.realsense_height,self.realsense_width,3),dtype=np.uint8)
        dmat=np.zeros((self.realsense_height,self.realsense_width,3),dtype=np.uint8)
        ctypescameraColorBuffer=cmat.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8*self.cameraBufferLength)).contents
        ctypescameraDepthBuffer=dmat.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8*self.cameraBufferLength)).contents
        
        self.cameraColorBuffer=RawArray('B',ctypescameraColorBuffer)
        self.cameraDepthBuffer=RawArray('B',ctypescameraDepthBuffer)
        
        cameraProcess=Process(target=self.camera.process,args=[self.cameraColorBuffer,self.cameraDepthBuffer])
        cameraProcess.start()
    def setup(self):
        self.initCamera()
        self.canvas=Canvas()

        pass
    def update(self):
        colorVec=np.ctypeslib.as_array(self.cameraColorBuffer)
        cameraColorMat=colorVec.reshape(self.realsense_height,self.realsense_width,3)
        depthVec=np.ctypeslib.as_array(self.cameraDepthBuffer)
        cameraDepthMat=depthVec.reshape(self.realsense_height,self.realsense_width,3)
        
        cv2.imshow("color",cameraColorMat)
        cv2.imshow("depth",cameraDepthMat)
        cv2.waitKey(1)
        pass
    pass



if __name__ == "__main__":
    main=Main()

    while True:
        stime=perf_counter()
        main.update()
        etime=perf_counter()
        print("Main time:",etime-stime)
    pass
