# 描画するキャンバスを管理
import cv2,ctypes
import numpy as np
from time import perf_counter
from EdeskModule.contentlib import ContentManager
from EdeskModule.detectorlib import Detector
# from multiprocessing import RawArray
class Canvas:
    projector_width=None
    projector_height=None
    canvas_width=None
    canvas_height=None
    projector_padding=None
    #最終的にimshowされるフレーム
    projectingMat=None
    #ここにコンテンツを書き込み，最終的にprojectingImageに埋め込む
    canvasMat=None

    contentManager=None
    detector=None
    def __init__(self,p_height,p_width,padding):
        #パラメータの初期化
        self.projector_height=p_height
        self.projector_width=p_width
        self.projector_padding=padding
        self.canvas_width=self.projector_width-self.projector_padding*2
        self.canvas_height=self.projector_height-self.projector_padding*2
        pass
    def setup(self):
        self.contentManager=ContentManager()
        #プロジェクタ用ウィンドウの初期化
        cv2.namedWindow('Projector',cv2.WINDOW_FULLSCREEN)
        cv2.imshow('Projector',self.projectingMat)
        cv2.moveWindow('Projector',0,0)
        cv2.resizeWindow('Projector',self.projector_width,self.projector_height)
        cv2.setMouseCallback('Projector',self.onProjectorClicked)
        pass
    def update(self):
        #各コンテンツの重ね合わせ


        contents=self.contentManager.editCanvas(self.canvasMat)
        contents=self.contentManager.getContents()
        for content in contents:
            pass
        self.canvasMat[:,:,2]+=1
        self.canvasMat[:,:,2]%=200

        self.projectingMat[self.projector_padding:self.projector_height-self.projector_padding,self.projector_padding:self.projector_width-self.projector_padding]=self.canvasMat
        cv2.imshow("Projector",self.projectingMat)
        cv2.waitKey(1)
        # print("Canvas.Update")
        pass
    def process(self,canvasBuffer,projectingBuffer,arucoResult,yoloResult):
        #ここに引数のarrayとフィールドのmatの関連付け処理を入れる
        #Realsenseクラスを参考
        cvec=np.ctypeslib.as_array(canvasBuffer)
        self.canvasMat=cvec.reshape(self.canvas_height,self.canvas_width,3)
        pvec=np.ctypeslib.as_array(projectingBuffer)
        self.projectingMat=pvec.reshape(self.projector_height,self.projector_width,3)
        
        #赤線を引くだけ
        self.projectingMat[self.projector_padding-1,:,2]=255
        self.projectingMat[self.projector_height-self.projector_padding+1,:,2]=255
        self.projectingMat[:,self.projector_padding-1,2]=255
        self.projectingMat[:,self.projector_width-self.projector_padding+1,2]=255
        self.setup()

        while True:
            stime=perf_counter()
            self.update()
            etime=perf_counter()
            # print("Canvas.update:",etime-stime)
        pass
    #プロジェクタの位置にウィンドウを移動
    def onProjectorClicked(self,event,x,y,flag,param):
        if event==cv2.EVENT_LBUTTONDOWN:
            cv2.moveWindow('Projector',0,0)
            cv2.resizeWindow('Projector',self.projector_width,self.projector_height)
            print('clicked Projector Window')