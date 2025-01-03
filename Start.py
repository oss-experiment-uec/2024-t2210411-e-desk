#!/usr/bin/env python3
# coding: utf-8

# OSS改変としての目標
# * プロジェクターの無い状態での動作を確かめられるようにする．
#   * 具体的にはノートPC一体のカメラ+projectorウィンドウ
#   * 何か変数を渡すとシミュレーションモードで立ち上がる．
#   * projectorウィンドウにカメラ映像を渡す．
#      * テーブル用ARマーカは紙に刷ってｋもらう?
#      * 各端に付与した状態にするのもあり． 
#   * あと，YOLOのモデルの作り直しとかもする?
# * なんか新しい機能ほしい．
#   * 
# * できるならRustとかC++で書き直すとかしてもいいかも．
# * 
## 最悪何か評価ができるという状況まで持っていければOK．
# * コンソール動作を前提に何かoutputするとか．

#これが新しいメイン
#python3 Start.pyで実行
import numpy as np
import argparse
import cv2
from cv2 import aruco
import multiprocessing
from EdeskModule.canvaslib import Canvas,VirtualCanvas
from EdeskModule.cameralib import Camera,RealSense,NormalCamera, VirtualCamera
from EdeskModule.detectorlib import ArucoDetector,yoloColorProcessFunction
from EdeskModule.contentlib import ContentManager
from EdeskModule.sharedObject import Constants
from multiprocessing import RawArray,Process,Manager,Event
import signal
from time import perf_counter,sleep
import ctypes
import argparse

class Main:

    c=None
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
    # yolo=None
    arucoProcess=None
    # yoloProcess=None
    yoloColorProcess=None
    def __init__(self):
        self.setup()
        pass
    def initCamera(self):
        self.camera=NormalCamera()
        # self.camera=NormalCamera()

        #Camera用Bufferの作成
        cmat=np.zeros((self.c.camera_height,self.c.camera_width,3),dtype=np.uint8)
        dmat=np.zeros((self.c.camera_height,self.c.camera_width,3),dtype=np.uint8)
        ctypescameraColorBuffer=cmat.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8*self.c.camera_length)).contents
        ctypescameraDepthBuffer=dmat.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8*self.c.camera_length)).contents
        
        self.cameraColorBuffer=RawArray('B',ctypescameraColorBuffer)
        self.cameraDepthBuffer=RawArray('B',ctypescameraDepthBuffer)
        
        
        pass
    def initCanvas(self):
        self.canvas=Canvas()

        cmat=np.zeros((self.c.canvas_height,self.c.canvas_width,3),dtype=np.uint8)
        dmat=np.zeros((self.c.projector_height,self.c.projector_width,3),dtype=np.uint8)
        ctypesCanvasBuffer=cmat.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8*self.c.canvas_length)).contents
        ctypesProjectingBuffer=dmat.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8*self.c.projector_length)).contents
        
        self.canvasBuffer=RawArray('B',ctypesCanvasBuffer)
        self.projectingBuffer=RawArray('B',ctypesProjectingBuffer)
        
        
    def initDetector(self):
        manager=Manager()
        #[color,depth]
        self.yoloResult=manager.list()
        #[corners,ids]
        self.arucoResult=manager.list()
        self.arucoResult.append([])
        self.arucoResult.append([])
        self.yoloResult.append(None)
        self.yoloResult.append(None)
        self.yoloResult.append(True)
        self.aruco=ArucoDetector()
        # self.yolo=YoloDetector()
        pass
    def setup(self):
        self.c=Constants()
        self.initCamera()
        self.initCanvas()
        self.initDetector()
        self.cameraProcess=Process(target=self.camera.process,args=[self.canvasBuffer,self.projectingBuffer,self.cameraColorBuffer,self.cameraDepthBuffer,self.arucoResult,self.yoloResult])
        self.cameraProcess.start()
        self.canvasProcess=Process(target=self.canvas.process,args=[self.canvasBuffer,self.projectingBuffer,self.cameraColorBuffer,self.cameraDepthBuffer,self.arucoResult,self.yoloResult])
        self.canvasProcess.start()
        self.arucoProcess=Process(target=self.aruco.process,args=[self.canvasBuffer,self.projectingBuffer,self.cameraColorBuffer,self.cameraDepthBuffer,self.arucoResult,self.yoloResult])
        # self.yoloProcess=Process(target=self.yolo.process,args=[self.canvasBuffer,self.projectingBuffer,self.cameraColorBuffer,self.cameraDepthBuffer,self.arucoResult,self.yoloResult])
        self.arucoProcess.start()
        # self.yoloProcess.start()
        self.yoloColorProcess=Process(target=yoloColorProcessFunction,args=[self.cameraColorBuffer,self.yoloResult])
        self.yoloColorProcess.start()
        pass
    def update(self):
        colorVec=np.ctypeslib.as_array(self.cameraColorBuffer)
        cameraColorMat=colorVec.reshape(self.c.camera_height,self.c.camera_width,3)
        depthVec=np.ctypeslib.as_array(self.cameraDepthBuffer)
        cameraDepthMat=depthVec.reshape(self.c.camera_height,self.c.camera_width,3)
        
        if self.c.DEBUG:
            # cv2.imshow("color",cameraColorMat)
            # cv2.imshow("depth",cameraDepthMat)
            # cv2.waitKey(1)
            # print("ArucoResult",self.arucoResult)
            pass
        # key=cv2.waitKey(1)


class SimMain:

    c=None
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
    # yolo=None
    arucoProcess=None
    # yoloProcess=None
    yoloColorProcess=None
    def __init__(self):
        self.setup()
        pass
    def initCamera(self):
        self.camera=VirtualCamera()
        
        #Camera用Bufferの作成
        cmat=np.zeros((self.c.camera_height,self.c.camera_width,3),dtype=np.uint8)
        dmat=np.zeros((self.c.camera_height,self.c.camera_width,3),dtype=np.uint8)
        ctypescameraColorBuffer=cmat.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8*self.c.camera_length)).contents
        ctypescameraDepthBuffer=dmat.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8*self.c.camera_length)).contents
        
        self.cameraColorBuffer=RawArray('B',ctypescameraColorBuffer)
        self.cameraDepthBuffer=RawArray('B',ctypescameraDepthBuffer)
        
        
        pass
    def initCanvas(self):
        self.canvas=VirtualCanvas()

        cmat=np.zeros((self.c.canvas_height,self.c.canvas_width,3),dtype=np.uint8)
        dmat=np.zeros((self.c.projector_height,self.c.projector_width,3),dtype=np.uint8)
        ctypesCanvasBuffer=cmat.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8*self.c.canvas_length)).contents
        ctypesProjectingBuffer=dmat.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8*self.c.projector_length)).contents
        
        self.canvasBuffer=RawArray('B',ctypesCanvasBuffer)
        self.projectingBuffer=RawArray('B',ctypesProjectingBuffer)
        
        
    def initDetector(self):
        manager=Manager()
        #[color,depth]
        self.yoloResult=manager.list()
        #[corners,ids]
        self.arucoResult=manager.list()
        self.arucoResult.append([])
        self.arucoResult.append([])
        self.yoloResult.append(None)
        self.yoloResult.append(None)
        self.yoloResult.append(True)
        self.aruco=ArucoDetector()
        # self.yolo=YoloDetector()
        pass
    def setup(self):
        self.c=Constants()
        self.initCamera()
        self.initCanvas()
        self.initDetector()
        self.cameraProcess=Process(target=self.camera.process,args=[self.canvasBuffer,self.projectingBuffer,self.cameraColorBuffer,self.cameraDepthBuffer,self.arucoResult,self.yoloResult,stop_flag])
        self.cameraProcess.start()
        self.canvasProcess=Process(target=self.canvas.process,args=[self.canvasBuffer,self.projectingBuffer,self.cameraColorBuffer,self.cameraDepthBuffer,self.arucoResult,self.yoloResult,stop_flag])
        self.canvasProcess.start()
        self.arucoProcess=Process(target=self.aruco.process,args=[self.canvasBuffer,self.projectingBuffer,self.cameraColorBuffer,self.cameraDepthBuffer,self.arucoResult,self.yoloResult,stop_flag])
        # self.yoloProcess=Process(target=self.yolo.process,args=[self.canvasBuffer,self.projectingBuffer,self.cameraColorBuffer,self.cameraDepthBuffer,self.arucoResult,self.yoloResult])
        self.arucoProcess.start()
        # self.yoloProcess.start()
        self.yoloColorProcess=Process(target=yoloColorProcessFunction,args=[self.cameraColorBuffer,self.yoloResult,stop_flag])
        self.yoloColorProcess.start()
        pass
    def update(self):
        colorVec=np.ctypeslib.as_array(self.cameraColorBuffer)
        cameraColorMat=colorVec.reshape(self.c.camera_height,self.c.camera_width,3)
        depthVec=np.ctypeslib.as_array(self.cameraDepthBuffer)
        cameraDepthMat=depthVec.reshape(self.c.camera_height,self.c.camera_width,3)
        
        if self.c.DEBUG:
            # cv2.imshow("color",cameraColorMat)
            # cv2.imshow("depth",cameraDepthMat)
            # cv2.waitKey(1)
            # print("ArucoResult",self.arucoResult)
            pass
        # key=cv2.waitKey(1)

def signalHandler(signal, handler) :
        stop_flag.set()


if __name__ == "__main__":
    stop_flag=Event()

    signal.signal(signal.SIGINT,  signalHandler)
    signal.signal(signal.SIGTERM, signalHandler)
    signal.signal(signal.SIGALRM, signalHandler)

    parser=argparse.ArgumentParser(
        description="The main program of e-desk"
    )
    parser.add_argument("--sim", help="e-desk simulation mode(beta)")
    args=parser.parse_args()

    if args.sim:
        main=SimMain()
        signal.alarm(1)
        while True:
            if stop_flag.is_set():
                break
            main.update()
        sleep(2)
    else:
        main=Main()
        while True:
            stime=perf_counter()
            main.update()
            etime=perf_counter()
            # print("Main time:",etime-stime)
        pass
