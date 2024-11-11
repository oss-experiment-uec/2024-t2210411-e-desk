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

from multiprocessing import RawArray,Process,Manager
from time import perf_counter
import ctypes

class Main:
    DEBUG=True
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

    #共有メモリは基本的にMainが保持，ContentsはキリがないのでContentsManagerで
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
    cameraProcess=None
    canvasProcess=None
    contentManagerProcess=None

    manager=None
    arucoResult=None
    yoloResult=None
    aruco=None
    yolo=None
    arucoProcess=None
    yoloProcess=None
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
        
        
        pass
    def initCanvas(self):
        self.canvas=Canvas(self.projector_height,self.projector_width,self.projector_padding)
        self.canvasBufferLength=self.canvas_height*self.canvas_width*3
        self.projectingBufferLength=self.projector_height*self.projector_width*3

        cmat=np.zeros((self.canvas_height,self.canvas_width,3),dtype=np.uint8)
        dmat=np.zeros((self.projector_height,self.projector_width,3),dtype=np.uint8)
        ctypesCanvasBuffer=cmat.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8*self.canvasBufferLength)).contents
        ctypesProjectingBuffer=dmat.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8*self.projectingBufferLength)).contents
        
        self.canvasBuffer=RawArray('B',ctypesCanvasBuffer)
        self.projectingBuffer=RawArray('B',ctypesProjectingBuffer)
        
        
    def initDetector(self):
        manager=Manager()
        self.yoloResult=manager.list()
        self.arucoResult=manager.list()
        self.arucoResult.append(None)
        self.arucoResult.append(None)
        self.aruco=ArucoDetector(self.realsense_width,self.realsense_height)
        self.yolo=YoloDetector(self.realsense_width,self.realsense_height)
        
        pass
    def setup(self):
        self.initCamera()
        self.initCanvas()
        self.initDetector()
        self.cameraProcess=Process(target=self.camera.process,args=[self.cameraColorBuffer,self.cameraDepthBuffer])
        self.cameraProcess.start()
        self.canvasProcess=Process(target=self.canvas.process,args=[self.canvasBuffer,self.projectingBuffer,self.arucoResult,self.yoloResult])
        self.canvasProcess.start()
        self.arucoProcess=Process(target=self.aruco.process,args=[self.arucoResult,self.cameraColorBuffer,self.cameraDepthBuffer])
        self.yoloProcess=Process(target=self.yolo.process,args=[self.yoloResult,self.cameraColorBuffer,self.cameraDepthBuffer])
        self.arucoProcess.start()
        self.yoloProcess.start()
        pass
    def update(self):
        colorVec=np.ctypeslib.as_array(self.cameraColorBuffer)
        cameraColorMat=colorVec.reshape(self.realsense_height,self.realsense_width,3)
        depthVec=np.ctypeslib.as_array(self.cameraDepthBuffer)
        cameraDepthMat=depthVec.reshape(self.realsense_height,self.realsense_width,3)
        
        if self.DEBUG:
            cv2.imshow("color",cameraColorMat)
            cv2.imshow("depth",cameraDepthMat)
            cv2.waitKey(1)
            # print("ArucoResult",self.arucoResult)
        pass
    pass



if __name__ == "__main__":
    main=Main()

    while True:
        stime=perf_counter()
        main.update()
        etime=perf_counter()
        # print("Main time:",etime-stime)
    pass
