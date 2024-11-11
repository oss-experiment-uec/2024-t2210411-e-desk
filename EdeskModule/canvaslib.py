# 描画するキャンバスを管理
import cv2,ctypes
import numpy as np
from time import perf_counter
from contentlib import ContentManager
# from multiprocessing import RawArray
class Canvas:
    width=None
    height=None
    #最終的にimshowされるフレーム
    projectingMat=None
    #ここにコンテンツを書き込み，最終的にprojectingImageに埋め込む
    canvasMat=None

    contentManager=None
    def __init__(self):
        pass
    def setup():
        pass
    def update():
        #各コンテンツの重ね合わせ
        #投影
        pass
    #キャンバスのx,yにimgを追加 
    def add():
        pass
    def getCanvas(self):
        pass
    def process(self):
        self.setup()
        #ここに引数のarrayとフィールドのmatの関連付け処理を入れる
        #Realsenseクラスを参考

        while True:
            self.update()
        pass