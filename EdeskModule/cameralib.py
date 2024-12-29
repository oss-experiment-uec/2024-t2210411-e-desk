import pyrealsense2 as rs
import cv2
import numpy as np
from time import perf_counter
import ctypes
from EdeskModule.sharedObject import Constants,MyProcess
# from multiprocessing import RawArray
class Camera(MyProcess):
    c=None
    def __init__(self):
        self.c=Constants()
        # self.length=self.c.camera_width*self.c.camera_height*3
        # self.color_image=np.zeros((self.c.camera_height,self.c.camera_width,3),dtype=np.uint8)
        # self.depth_image=np.zeros((self.c.camera_height,self.c.camera_width,3),dtype=np.uint8)
        # self.cameraColorMat=np.zeros((self.c.camera_height,self.c.camera_width,3),dtype=np.uint8)
        # self.cameraDepthMat=np.zeros((self.c.camera_height,self.c.camera_width,3),dtype=np.uint8)
        # # self.connect()
        pass
    def setup(self):
        self.connect()
        pass
    def connect(self):
        pass
    def disconnect(self):
        pass
    def update(self):
        super.update()
        pass

    pass
class RealSense(Camera):
    
    
    #ここの記述は公式?デモほぼそのまま
    def connect(self):
        # Configure depth and color streams
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        # Get device product line for setting a supporting resolution
        self.pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
        self.pipeline_profile = self.config.resolve(self.pipeline_wrapper)
        self.device = self.pipeline_profile.get_device()
        self.device_product_line = str(self.device.get_info(rs.camera_info.product_line))

        #接続の確認
        self.found_rgb = False
        for s in self.device.sensors:
            if s.get_info(rs.camera_info.name) == 'RGB Camera':
                self.found_rgb = True
                break
        if not self.found_rgb:
            print("The demo requires Depth camera with Color sensor")
            exit(0)

        # config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        self.config.enable_stream(rs.stream.depth, self.c.camera_width, self.c.camera_height, rs.format.z16, self.c.camera_fps)
        # config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        self.config.enable_stream(rs.stream.color, self.c.camera_width, self.c.camera_height, rs.format.bgr8, self.c.camera_fps)
        # Start streaming
        self.pipeline.start(self.config)

        print("Camera:success to connect the camera!")
        pass
    def disconnect(self):
        self.pipeline.stop()
        self.config.disable_all_streams()
        pass
    def update(self):
        stime=perf_counter()
        # Wait for a coherent pair of frames: depth and color
        self.frames = self.pipeline.wait_for_frames()
        print(type(self.frames))
        self.depth_frame = self.frames.get_depth_frame()
        self.color_frame = self.frames.get_color_frame()
        print(type(self.color_frame))
        if not self.depth_frame or not self.color_frame:
            print("Camera:cannot get frame")
            return
        pass
        # Convert images to numpy arrays
        self.depth_image = np.asanyarray(self.depth_frame.get_data())
        self.color_image = np.asanyarray(self.color_frame.get_data())
        self.write2Buffer()
        etime=perf_counter()
        # print("Camera.update():",etime-stime)
    def write2Buffer(self):
        np.copyto(self.cameraColorMat,self.color_image)
        #デバッグ用
        # cv2.imshow("cameralib",self.cameraColorMat)
        # cv2.waitKey(1)

class VirtualCamera(Camera):
    capture=None
    def connect(self):
        self.capture=cv2.VideoCapture('VirtualDesk.png')
        if self.capture.isOpened():
            print("Success to open virtual camera!!!")
        else:
            print("Failed to open virtual camera...")
        pass
    def disconnect(self):
        pass
    def update(self):
        (ret,frame)=self.capture.read()
        if ret:
            # print("NormalCamera.Update:Get Data!!!")
            self.color_image=cv2.resize(frame,(self.c.camera_width,self.c.camera_height))
            self.depth_image=self.color_image

            self.write2Buffer()
            pass
        else:
            # print("NormalCamera.Update:No data")
            pass
    def write2Buffer(self):
        np.copyto(self.cameraColorMat,self.color_image)
        np.copyto(self.cameraDepthMat,self.depth_image)
        pass


class NormalCamera(Camera):
    capture=None
    def connect(self):
        self.capture=cv2.VideoCapture(self.c.cameraID)
        if self.capture.isOpened():
            print("Success to open normal camera!!!")
        else:
            print("Failed to open normal camera...")
        pass
    def disconnect(self):
        pass
    def update(self):
        (ret,frame)=self.capture.read()
        if ret:
            # print("NormalCamera.Update:Get Data!!!")
            self.color_image=cv2.resize(frame,(self.c.camera_width,self.c.camera_height))
            self.depth_image=self.color_image

            self.write2Buffer()
            pass
        else:
            # print("NormalCamera.Update:No data")
            pass
    def write2Buffer(self):
        np.copyto(self.cameraColorMat,self.color_image)
        np.copyto(self.cameraDepthMat,self.depth_image)
        pass
