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
    prevkey=0
    prevYoloCls=-1
    noHandFrame=0
    noHandTimeout=5
    def __init__(self):
        self.c=Constants()
        #射影変換用の対応する4点．ARマーカの位置で適宜更新
        self.camera_corners=np.array([[0,0],[self.c.camera_width,0],[self.c.camera_width,self.c.camera_height],[0,self.c.camera_height]],dtype='float32')
        self.canvas_corners=np.array([[0,0],[self.c.canvas_width,0],[self.c.canvas_width,self.c.canvas_height],[0,self.c.canvas_height]],dtype='float32')

        pass
    def initWindow(self):
        cv2.namedWindow('Projector',cv2.WINDOW_FULLSCREEN)
        cv2.imshow('Projector',self.projectingMat)
        cv2.moveWindow('Projector',0,0)
        cv2.resizeWindow('Projector',self.c.projector_width,self.c.projector_height)
        cv2.setMouseCallback('Projector',self.onProjectorClicked)
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
        self.initWindow()
        
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
            #Videoであれば映像を更新
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
            pass

        #Yolo
        if self.yoloResult[0] is not None:
            result_color_boxes=self.yoloResult[0]
            noHand=True
            for i in range(0,len(result_color_boxes.cls)):
                noHand=False
                cls=result_color_boxes.cls[i]
                xyxy=result_color_boxes.xyxy[i]
                xy1_after=cv2.perspectiveTransform(np.array([[(xyxy[0]*2,xyxy[1]*2)]]),mat_camera2canvas)
                xy2_after=cv2.perspectiveTransform(np.array([[(xyxy[2]*2,xyxy[3]*2)]]),mat_camera2canvas)
                if cls==1:
                    self.prevYoloCls=1
                    # mx=(xy1_after[0][0][0]+xy2_after[0][0][0])/2        
                    # my=(xy1_after[0][0][1]+xy2_after[0][0][1])/2
                    # cv2.putText(self.canvasMat,"C",(int(mx),int(my)),cv2.FONT_HERSHEY_COMPLEX,2.0,(0,0,255),thickness=3) 
                    pass
                elif cls==0:
                    self.prevYoloCls=0
                elif cls==2:
                    if self.prevYoloCls==0:
                        self.contentManager.changeImage()
                    self.prevYoloCls=2
                cv2.rectangle(self.canvasMat,(int(xy1_after[0][0][0]),int(xy1_after[0][0][1])),(int(xy2_after[0][0][0]),int(xy2_after[0][0][1])),self.c.result_boxcolors[int(cls)],thickness=5)
            if noHand: #一定フレーム間noHandだったときの処理
                self.noHandFrame+=1
                if self.noHandFrame>=self.noHandTimeout:
                    self.prevYoloCls=-1

        cv2.imshow("Canvas",self.canvasMat)

        self.projectingMat[self.c.projector_padding:self.c.projector_height-self.c.projector_padding,self.c.projector_padding:self.c.projector_width-self.c.projector_padding]=self.canvasMat
        cv2.imshow("Projector",self.projectingMat)
        key=cv2.waitKey(1)
        # print(key)
        # if key==99 and self.prevkey != 99:
        #     self.yoloResult[2]=not self.yoloResult[2]
        #ここにelifでつなげてkey
        self.prevUpdatetime=perf_counter()
        self.prevkey=key
        pass


    #クリックしたらプロジェクタの位置にウィンドウを移動
    def onProjectorClicked(self,event,x,y,flag,param):
        if event==cv2.EVENT_LBUTTONDOWN:
            cv2.moveWindow('Projector',0,0)
            cv2.resizeWindow('Projector',self.projector_width,self.projector_height)
            print('clicked Projector Window')
            self.yoloResult[2]=not self.yoloResult[2]