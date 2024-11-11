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
    width_realsense=1280
    height_realsense=720
    fps_realsense=30

    padding_projector=80
    #1d-Array(ctype),こいつが共有メモリ 
    colorBuffer=None
    depthBuffer=None
    #ctypeだとOpenCVで扱いにくいのでndarrayに変更．ただし同じデータを指すポインタになっているはず
    colorMat=None
    depthMat=None

    camera=None
    def __init__(self):
        self.setup()
        pass
    def initCamera(self):
        self.camera=NormalCamera(self.width_realsense,self.height_realsense,self.fps_realsense)
        # self.camera=RealSense(self.width_realsense,self.height_realsense,self.fps_realsense)
        self.cameraBufferLength=self.width_realsense*self.height_realsense*3
        
        #Camera用Bufferの作成
        cmat=np.zeros((self.height_realsense,self.width_realsense,3),dtype=np.uint8)
        dmat=np.zeros((self.height_realsense,self.width_realsense,3),dtype=np.uint8)
        ctypesColorBuffer=cmat.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8*self.cameraBufferLength)).contents
        ctypesDepthBuffer=dmat.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8*self.cameraBufferLength)).contents
        
        self.colorBuffer=RawArray('B',ctypesColorBuffer)
        self.depthBuffer=RawArray('B',ctypesDepthBuffer)
        
        cameraProcess=Process(target=self.camera.process,args=[self.colorBuffer,self.depthBuffer])
        cameraProcess.start()
    def setup(self):
        self.initCamera()
        self.canvas=Canvas()

        pass
    def update(self):
        colorVec=np.ctypeslib.as_array(self.colorBuffer)
        colorMat=colorVec.reshape(self.height_realsense,self.width_realsense,3)
        depthVec=np.ctypeslib.as_array(self.depthBuffer)
        depthMat=depthVec.reshape(self.height_realsense,self.width_realsense,3)
        
        cv2.imshow("color",colorMat)
        cv2.imshow("depth",depthMat)
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
