import cv2
from EdeskModule.sharedObject import Constants,MyProcess
import numpy as np
import signal
from time import perf_counter
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
    
    def __init__(self,path,id):
        super().__init__()
        fullpath=self.c.contents_path+path
        self.capture=cv2.VideoCapture(fullpath)
        #if エラーチェック
        if not self.capture.isOpened():
            print("Cannot open Video:",fullpath)
        self.id=id
        self.width=self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height=self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.corner_before=np.zeros((4,2), dtype='float32')
        self.corner_after=np.zeros((4,2), dtype='float32')
        self.corner_before[0]=np.array([0,0],dtype='float32')
        self.corner_before[1]=np.array([self.width,0],dtype='float32')
        self.corner_before[2]=np.array([self.width,self.height],dtype='float32')
        self.corner_before[3]=np.array([0,self.height],dtype='float32')
        print("content:",(id,self.width,self.height))
    def getType(self):
        return 1
    def update(self):
        ctime=perf_counter()
        if ctime-self.prevtime>=1/300:
            (ret,self.frame)=self.capture.read()
            # :print("content update",ctime-self.prevtime)
            if not ret:
                self.capture.set(cv2.CAP_PROP_POS_FRAMES,0)
                ret,self.frame=self.capture.read()
            self.prevtime=ctime

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

class VariableImage(Content):
    image1 = None
    image2 = None
    current_is_1 = True
    def __init__(self, path1, path2, id):
        super().__init__()
        fullpath1=self.c.contents_path+path1
        fullpath2=self.c.contents_path+path2
        self.image1=cv2.imread(fullpath1)
        self.image2=cv2.imread(fullpath2)
        self.id=id
        self.width=self.image1.shape[1]
        self.height=self.image1.shape[0]
        self.corner_before=np.zeros((4,2), dtype='float32')
        self.corner_after=np.zeros((4,2), dtype='float32')
        self.corner_before[0]=np.array([0,0],dtype='float32')
        self.corner_before[1]=np.array([self.width,0],dtype='float32')
        self.corner_before[2]=np.array([self.width,self.height],dtype='float32')
        self.corner_before[3]=np.array([0,self.height],dtype='float32')
        print("content:",(id,self.width,self.height))
        self.image2 = cv2.resize(self.image2, (self.width, self.height))
        self.frame=self.image1
        pass
    def getType(self):
        return 2
    pass

    def setup(self):

        pass

    def changeframe(self):
        if self.current_is_1:
            self.frame = self.image2
            self.current_is_1=False
        else: 
            self.frame = self.image1
            self.current_is_1=True
        pass
    
    def getframe(self):
        return self.frame

class ContentManager:
    c=None
    contentsArray:list[Content]=[]
    
    def setup(self):
        self.c=Constants()
        for i in range(0,self.c.N_CONTENTS):
            if self.c.contentsType[i]==0:
                self.contentsArray.append(Image(self.c.contentsFile[i],i))
            elif self.c.contentsType[i]==1: #video
                self.contentsArray.append(Video(self.c.contentsFile[i],i))
            elif self.c.contentsType[i]==2: #changableImage
                self.contentsArray.append(VariableImage(self.c.changeImageFile[0],self.c.changeImageFile[1],i))
        pass
    def update(self):
        pass
    pass
    def getContents(self):
        return self.contentsArray
    def changeImage(self):
        for content in self.contentsArray:
            if content.getType()==2:
                content.changeframe()
        pass