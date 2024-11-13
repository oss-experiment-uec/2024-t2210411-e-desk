# 描画するキャンバスを管理
import cv2,ctypes
import numpy as np
from time import perf_counter
from EdeskModule.contentlib import ContentManager,Content
from EdeskModule.detectorlib import Detector
from EdeskModule.sharedObject import MyProcess,Constants
# from multiprocessing import RawArray
class Canvas(MyProcess):
    c=None
    camera_corners=None
    canvas_corners=None

    contentManager=None
    detector=None
    prevUpdatetime=0.0
    def __init__(self):
        self.c=Constants()
        #射影変換用の対応する4点．ARマーカの位置で適宜更新
        self.camera_corners=np.array([[0,0],[self.c.camera_width,0],[self.c.camera_width,self.c.camera_height],[0,self.c.camera_height]],dtype='float32')
        self.canvas_corners=np.array([[0,0],[self.c.canvas_width,0],[self.c.canvas_width,self.c.canvas_height],[0,self.c.canvas_height]],dtype='float32')

        pass
    def setup(self):
        self.contentManager=ContentManager()
        self.contentManager.setup()
        #赤線を引くだけ
        self.projectingMat[self.projector_padding-1,:,2]=255
        self.projectingMat[self.projector_height-self.projector_padding+1,:,2]=255
        self.projectingMat[:,self.projector_padding-1,2]=255
        self.projectingMat[:,self.projector_width-self.projector_padding+1,2]=255
        
        #プロジェクタ用ウィンドウの初期化
        cv2.namedWindow('Projector',cv2.WINDOW_FULLSCREEN)
        cv2.imshow('Projector',self.projectingMat)
        cv2.moveWindow('Projector',0,0)
        cv2.resizeWindow('Projector',self.c.projector_width,self.c.projector_height)
        cv2.setMouseCallback('Projector',self.onProjectorClicked)

        self.prevUpdatetime=perf_counter()
        pass
    def update(self):
        #arucoResultは勝手に書き換わる
        #キャリブレーション処理
        arucoCorners=self.arucoResult[0]
        arucoIds=self.arucoResult[1]
        print(arucoCorners)
        print(arucoIds)
        print("------")
        for i in range(0,len(arucoCorners)):
            if arucoIds is None or len(arucoCorners)!=len(arucoIds):
                print("arucoId is wrong")
                break
            if arucoIds[i]//4==0:#キャリブレーション用の4隅
                self.camera_corners[arucoIds[i]]=arucoCorners[i][0][0] #id番目の0個目のマーカーの左上
        
        mat_camera2canvas = cv2.getPerspectiveTransform(self.camera_corners,self.canvas_corners )#変換行列を求める

        canvas_after = cv2.warpPerspective(self.cameraColorMat, mat_camera2canvas, (self.c.canvas_width, self.c.canvas_height)) #射影変換後の画像
        cv2.imshow("Desk",canvas_after)


        contents:list[Content]=self.contentManager.getContents()
        #マーカの登録
        #一旦disableにする作業
        ctime=perf_counter()
        for content in contents:
            content.waittime+=ctime-self.prevUpdatetime
            if content.waittime>=self.c.TIMEOUT:
                content.setDisable()
        #見つかったマーカを処理
        for i in range(0,len(arucoCorners)):
            if arucoIds is None or len(arucoCorners)!=len(arucoIds):
                print("arucoId is wrong")
                break
            if arucoIds[i]//4>0 and arucoIds[i]//4<=self.c.N_CONTENTS:
                contentsid=arucoIds[i][0]//4-1
                cornerid=arucoIds[i][0]%4 #左上左下右下右上のどれか
                print(arucoIds)
                print(contentsid)
                contents[contentsid].setEnable() #見つかったらEnable
                corner_after=cv2.perspectiveTransform(np.array([[arucoCorners[i][0][0]]]),mat_camera2canvas)#座標変換
                contents[contentsid].corner_after[cornerid]=corner_after[0][0]
            pass
        #各コンテンツの重ね合わせ
        self.canvasMat[:,:,:]=0
        for content in contents:
            if content.getType()==self.c.videoType:
                content.update()
            if content.enable:
                content_mat=content.getPerspectiveMat()
                content_frame=cv2.warpPerspective(content.frame, content_mat,(self.c.canvas_width,self.c.canvas_height))
                gray=cv2.cvtColor(content_frame,cv2.COLOR_BGR2GRAY)
                ret,mask=cv2.threshold(gray,10,255,cv2.THRESH_BINARY)
                mask_inv=cv2.bitwise_not(mask)
                np.copyto(self.canvasMat,cv2.bitwise_and(self.canvasMat,self.canvasMat,mask=mask_inv))
                content_masked=cv2.bitwise_and(content_frame,content_frame,mask=mask)
                np.copyto(self.canvasMat,cv2.add(self.canvasMat,content_masked))
                # print("add:",content.id)
                # cv2.imshow("frame",content_frame)
                # cv2.imshow("content",content.frame)

            pass
        cv2.imshow("Canvas",self.canvasMat)
        cv2.waitKey(1)
        # print(self.yoloResult)
        # self.canvasMat[:,:,2]+=1
        # self.canvasMat[:,:,2]%=200

        self.projectingMat[self.c.projector_padding:self.c.projector_height-self.c.projector_padding,self.c.projector_padding:self.c.projector_width-self.c.projector_padding]=self.canvasMat
        cv2.imshow("Projector",self.projectingMat)
        cv2.waitKey(1)
        # print("Canvas.Update")
        self.prevUpdatetime=perf_counter()
        pass


    #プロジェクタの位置にウィンドウを移動
    def onProjectorClicked(self,event,x,y,flag,param):
        if event==cv2.EVENT_LBUTTONDOWN:
            cv2.moveWindow('Projector',0,0)
            cv2.resizeWindow('Projector',self.projector_width,self.projector_height)
            print('clicked Projector Window')