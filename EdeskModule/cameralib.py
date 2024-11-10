import pyrealsense2 as rs
import cv2
import numpy as np
from time import perf_counter
class Camera:
    def __init__(self,width,height,fps):
        self.width=width
        self.height=height
        self.fps=fps
        self.connect()
        pass
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
        self.config.enable_stream(rs.stream.depth, self.width, self.height, rs.format.z16, self.fps)
        # config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        self.config.enable_stream(rs.stream.color, self.width, self.height, rs.format.bgr8, self.fps)

        # Start streaming
        self.pipeline.start(self.config)

        print("Camera:success to connect the camera!")
        pass
    def disconnect():
        pass
    #共有メモリを登録
    def setBuffer(self,buf):
        self.rawBuffer=buf
        pass
    def update(self):
        stime=perf_counter()
        # Wait for a coherent pair of frames: depth and color
        self.frames = self.pipeline.wait_for_frames()
        self.depth_frame = self.frames.get_depth_frame()
        self.color_frame = self.frames.get_color_frame()
        if not self.depth_frame or not self.color_frame:
            print("Camera:cannot get frame")
            return
        pass
        # Convert images to numpy arrays
        self.depth_image = np.asanyarray(self.depth_frame.get_data())
        self.color_image = np.asanyarray(self.color_frame.get_data())
        # images = np.hstack((self.color_image, self.depth_image))

        cv2.imshow('color', self.color_image)
        cv2.imshow('depth', self.depth_image)
        cv2.waitKey(1)
        etime=perf_counter()
        print("Camera.update():",etime-stime)
