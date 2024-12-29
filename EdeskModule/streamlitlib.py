import numpy as np
import streamlit as st
from streamlit_webrtc import webrtc_streamer
import av
import cv2
from time import perf_counter
import ctypes
from EdeskModule.sharedObject import Constants,MyProcess

class Streamlit(MyProcess):
    c=None
    def __init__(self):
        self.c=Constants()
        st.title("E-desk Sim")
        webrtc_streamer(key="Camv", video_frame_callback=self.callback)
        pass
    def setup(self):
        self.connect()
        pass
    def callback(frame, self):
        self.color_image=cv2.resize((frame.to_ndarray(format="bgr24"),(self.c.camera_width,self.c.camera_height)))
        self.write2Buffer()
        return av.videoFrame.from_ndarray(self.projectingMat, format="bgr24")
    def connect(self):
        pass
    def disconnect(self):
        pass
    def write2Buffer(self):
        np.copyto(self.cameraColorMat,self.color_image)
    def update(self):
        super.update()
        pass

    pass


