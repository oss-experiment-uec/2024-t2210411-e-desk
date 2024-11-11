import cv2

#コンテンツクラス
class Contents:
    def __init__(self):
        self.x=0
        self.y=0
        self.w=0
        self.h=0
        pass
    def update():
        pass
    #Imageなら0，Videoなら1
    def getType():
        print("Warning:content.getTypeが呼ばれています")
        return 0

class Video(Contents):
    def getType(self):
        return 1
    pass
class Image(Contents):
    def getType(self):
        return 0
    pass

class ContentManager:
    N_CONTENTS=3
    contentsType=[0,1,0]
    contentsFile=["Meros.png","anime.webm","face.jpg"]
    contentsArray=[]
    def setup(self):
        for i in range(0,self.N_CONTENTS):
            if self.contentsType==0:
                self.contentsArray.append(Image(self.contentsFile[i]))
            else:
                self.contentsArray.append(Video(self.contentsFile[i]))
        pass
    def update(self):
        # print("ContentManager:update")
        pass
    def editCanvas(self,canvasMat,arcuoResult=None,YoloResult=None):
        canvasMat[:,:,0]+=1
        canvasMat[:,:,0]%=200
        # print("ContentManager:Edited canvas")
        pass
    pass
    def getContents(self):
        return self.contentsArray