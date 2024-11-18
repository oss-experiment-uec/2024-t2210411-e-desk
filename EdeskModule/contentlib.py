import cv2
from EdeskModule.sharedObject import Constants,MyProcess
import numpy as np
from time import perf_counter
from multiprocessing import Process,RawArray
import ctypes
#コンテンツクラス
class Content:
    c=None
    frame=None
    id=None
    corner_before=None #射影変換の4点
    corner_after=None  #射影変換の4点
    width=0
    height=0
    enable=False #投影中かどうか
    waittime=0.0 #N秒マーカが見つからなかったらTimeout
    mat_perspective=None
    def __init__(self):
        self.c=Constants()
        
        pass
    def update():
        pass
    #Imageなら0，Videoなら1
    def getType():
        print("Warning:content.getTypeが呼ばれています")
        return 0
    def setEnable(self):
        self.enable=True
        self.waittime=0.0
    def setDisable(self):
        self.enable=False
    def isEnable(self):
        return self.enable
    def getPerspectiveMat(self):
        return cv2.getPerspectiveTransform(self.corner_before,self.corner_after)
class Video(Content):
    capture=None
    prevtime=0
    pProcess=None
    VideoBuffer=None
    vmat=None
    fullpath=None
    def __init__(self,path,id):
        super().__init__()
        self.fullpath=self.c.contents_path+path
        self.capture=cv2.VideoCapture(self.fullpath)
        #if エラーチェック
        if not self.capture.isOpened():
            print("Cannot open Video:",self.fullpath)
        self.id=id
        self.width=int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height=int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.corner_before=np.zeros((4,2), dtype='float32')
        self.corner_after=np.zeros((4,2), dtype='float32')
        self.corner_before[0]=np.array([0,0],dtype='float32')
        self.corner_before[1]=np.array([self.width,0],dtype='float32')
        self.corner_before[2]=np.array([self.width,self.height],dtype='float32')
        self.corner_before[3]=np.array([0,self.height],dtype='float32')
        print("content:",(id,self.width,self.height))
        self.capture.release()
        #Video用Bufferの作成
        vmat=np.zeros((self.height,self.width,3),dtype=np.uint8)
        vlength=self.width*self.height*3
        ctypesVideoBuffer=vmat.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8*vlength)).contents
        
        self.VideoBuffer=RawArray('B',ctypesVideoBuffer)
        
        self.pProcess=Process(target=self.process,args=[self.VideoBuffer])
        self.pProcess.start()
    def getType(self):
        return 1
    def update(self):
        #共有メモリからframeへコピー
        np.copyto(self.frame,self.vmat)
        pass
    def processSetup(self,cap):
        pass
    def processUpdate(self,cap,videoMat,prevtime):
        ctime=perf_counter()
        if ctime-prevtime>=1/23:
            (ret,mat)=cap.read()
            np.copyto(videoMat,mat)
            cv2.imshow("video",videoMat)
            cv2.waitKey(1)
            # :print("content update",ctime-self.prevtime)
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES,0)
                ret,mat=cap.read()
                np.copyto(videoMat,mat)
            return perf_counter()
        return prevtime
    def process(self,videoBuffer):
        cvec=np.ctypeslib.as_array(videoBuffer)
        videoMat=cvec.reshape(self.height,self.width,3)
        cap=cv2.VideoCapture(self.fullpath)
        #if エラーチェック
        if not cap.isOpened():
            print("Cannot open Video in SubProcess:",self.fullpath)
        self.processSetup(cap)
        prevtime=0
        while True:
            prevtime=self.processUpdate(cap,videoMat,prevtime)
        pass
    pass
class Image(Content):
    def __init__(self,path,id):
        super().__init__()
        fullpath=self.c.contents_path+path
        self.frame=cv2.imread(fullpath)
        self.id=id
        self.width=self.frame.shape[1]
        self.height=self.frame.shape[0]
        self.corner_before=np.zeros((4,2), dtype='float32')
        self.corner_after=np.zeros((4,2), dtype='float32')
        self.corner_before[0]=np.array([0,0],dtype='float32')
        self.corner_before[1]=np.array([self.width,0],dtype='float32')
        self.corner_before[2]=np.array([self.width,self.height],dtype='float32')
        self.corner_before[3]=np.array([0,self.height],dtype='float32')
        print("content:",(id,self.width,self.height))

        pass
    def getType(self):
        return 0
    pass
    def setup(self):

        pass
    def getFrame(self):
        return self.frame
class ContentManager:
    c=None
    contentsArray=[]
    
    def setup(self):
        self.c=Constants()
        for i in range(0,self.c.N_CONTENTS):
            if self.c.contentsType[i]==0:
                self.contentsArray.append(Image(self.c.contentsFile[i],i))
            else:
                self.contentsArray.append(Video(self.c.contentsFile[i],i))
        pass
    def update(self):
        pass
    pass
    def getContents(self):
        return self.contentsArray