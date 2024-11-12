# 描画するキャンバスを管理
import cv2,ctypes
import numpy as np
from time import perf_counter
from EdeskModule.contentlib import ContentManager
from EdeskModule.detectorlib import Detector
from EdeskModule.sharedObject import MyProcess,Constants
# from multiprocessing import RawArray
class Canvas(MyProcess):
    c=None
    camera_corners=None
    canvas_corners=None

    contentManager=None
    detector=None
    def __init__(self):
        self.c=Constants()
        #射影変換用の対応する4点．ARマーカの位置で適宜更新
        self.camera_corners=np.array([[0,0],[self.c.camera_width,0],[self.c.camera_width,self.c.camera_height],[0,self.c.camera_height]],dtype='float32')
        self.canvas_corners=np.array([[0,0],[self.c.canvas_width,0],[self.c.canvas_width,self.c.canvas_height],[0,self.c.canvas_height]],dtype='float32')

        pass
    def setup(self):
        self.contentManager=ContentManager()
        #プロジェクタ用ウィンドウの初期化
        cv2.namedWindow('Projector',cv2.WINDOW_FULLSCREEN)
        cv2.imshow('Projector',self.projectingMat)
        cv2.moveWindow('Projector',0,0)
        cv2.resizeWindow('Projector',self.c.projector_width,self.c.projector_height)
        cv2.setMouseCallback('Projector',self.onProjectorClicked)
        pass
    def update(self):
        #arucoResultは勝手に書き換わる
        #キャリブレーション処理
        arucoCorners=self.arucoResult[0]
        arucoIds=self.arucoResult[1]
        for i in range(0,len(arucoCorners)):
            if arucoIds[i]//4==0:#キャリブレーション用の4隅
                self.camera_corners[arucoIds[i]]=arucoCorners[i][0][0] #id番目の0個目のマーカーの左上
        
        mat_camera2canvas = cv2.getPerspectiveTransform(self.camera_corners,self.canvas_corners )#変換行列を求める

        # canvas_after = cv2.warpPerspective(self.cameraMAt, mat_camera2canvas, (width_canvas, height_canvas)) #射影変換後の画像
        # cv2.imshow("Desk",canvas_after)
        #各コンテンツの重ね合わせ
        contents=self.contentManager.editCanvas(self.canvasMat)
        contents=self.contentManager.getContents()
        for content in contents:
            pass

        
        # self.canvasMat[:,:,2]+=1
        # self.canvasMat[:,:,2]%=200

        self.projectingMat[self.c.projector_padding:self.c.projector_height-self.c.projector_padding,self.c.projector_padding:self.c.projector_width-self.c.projector_padding]=self.canvasMat
        cv2.imshow("Projector",self.projectingMat)
        cv2.waitKey(1)
        # print("Canvas.Update")
        pass


    #あとで消す，赤線だけ残す
    def process(self,canvasBuffer,projectingBuffer,cameraColorBuffer,cameraDepthBuffer,arucoResult,yoloResult):
        #ここに引数のarrayとフィールドのmatの関連付け処理を入れる
        #Realsenseクラスを参考
        cvec=np.ctypeslib.as_array(canvasBuffer)
        self.canvasMat=cvec.reshape(self.canvas_height,self.canvas_width,3)
        pvec=np.ctypeslib.as_array(projectingBuffer)
        self.projectingMat=pvec.reshape(self.projector_height,self.projector_width,3)
        cvec=np.ctypeslib.as_array(cameraColorBuffer)
        self.cameraColorBuffer=cvec.reshape(self.camera_height,self.camera_width,3)
        dvec=np.ctypeslib.as_array(cameraDepthBuffer)
        self.cameraDepthBuffer=dvec.reshape(self.camera_height,self.camera_width,3)
        self.yoloResult=yoloResult
        self.arucoResult=arucoResult
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