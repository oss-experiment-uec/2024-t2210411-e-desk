#このコードを参考に処理を分けていく

#!/usr/bin/python3

## License: Apache 2.0. See LICENSE file in root directory.
## Copyright(c) 2015-2017 Intel Corporation. All Rights Reserved.

###############################################
##      Open CV and Numpy integration        ##
###############################################

import pyrealsense2 as rs
import numpy as np
import cv2
from cv2 import aruco
from ultralytics import YOLO
import multiprocessing



#load images
background_img=cv2.imread('./contents/background.jpg')
background_img=cv2.flip(background_img,-1)

contents_length=4
textpage=0
bookimg=cv2.imread('./contents/Meros.png')
textbookimg=cv2.imread('./contents/textbook'+str(textpage)+'.png')
faceimg=cv2.imread('./contents/face.jpg')
cap=cv2.VideoCapture('./contents/sm1751094.mp4')
ret,frame=cap.read()
contentsimg=[textbookimg, bookimg,frame,faceimg]
contents_enable=np.zeros(contents_length,dtype='bool')
contents_isvideo=np.zeros(contents_length,dtype='bool')
contents_isvideo[1]=True
contents_capture=[None for i in range(0,contents_length)]
contents_capture[1]=cap
contents_corners_after=np.zeros((contents_length,4,2), dtype='float32')
contents_corners_before=np.zeros((contents_length,4,2), dtype='float32')
for i in range(0,contents_length):
    w=contentsimg[i].shape[1]
    h=contentsimg[i].shape[0]
    contents_corners_before[i,0]=np.array([0,0],dtype='float32')
    contents_corners_before[i,1]=np.array([w,0],dtype='float32')
    contents_corners_before[i,2]=np.array([w,h],dtype='float32')
    contents_corners_before[i,3]=np.array([0,h],dtype='float32')



coloron=False
depthon=False


#main loop
while True:



    # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
    depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.2), cv2.COLORMAP_JET)

    # detect AR markers
    corners, ids, rejectedImgPoints = aruco.detectMarkers(color_image, dict_aruco)
    aruco.drawDetectedMarkers(color_image,corners,ids)
    # print(ids)
    

    contents_enable=np.zeros(contents_length,dtype='bool')#一度falseで初期化
    for i in range(0,len(corners)):
        if ids[i]//4>0 and ids[i]//4<=contents_length:
            contentsid=ids[i]//4-1
            cornerid=ids[i]%4
            contents_enable[contentsid]=True
            corner_after=cv2.perspectiveTransform(np.array([[corners[i][0][0]]]),mat)#座標変換
            contents_corners_after[contentsid,cornerid]=corner_after[0][0]

    canvas=np.zeros((height_canvas,width_canvas,3),dtype='uint8')
    for i in range(0,contents_length):
        if contents_enable[i]==True:

            content_mat=cv2.getPerspectiveTransform(contents_corners_before[i],contents_corners_after[i] )
            content_after=cv2.warpPerspective(contentsimg[i], content_mat,(width_canvas,height_canvas))
            gray=cv2.cvtColor(content_after,cv2.COLOR_BGR2GRAY)
            ret,mask=cv2.threshold(gray,10,255,cv2.THRESH_BINARY)
            mask_inv=cv2.bitwise_not(mask)
            canvas=cv2.bitwise_and(canvas,canvas,mask=mask_inv)
            content_masked=cv2.bitwise_and(content_after,content_after,mask=mask)
            canvas=cv2.add(canvas,content_masked)
            # projectimg[padding_projector:height_projector-padding_projector,padding_projector:width_projector-padding_projector]=content_after
            if contents_isvideo[i]:
                ret,contentsimg[i]=contents_capture[i].read()
                if not ret:
                    contents_capture[i].set(cv2.CAP_PROP_POS_FRAMES,0)
                    ret,contentsimg[i]=contents_capture[i].read()
            

    depth_small=cv2.resize(depth_colormap,None,fx=0.5,fy=0.5)
    color_small=cv2.resize(color_image,None,fx=0.5,fy=0.5)

    depth_gray = (depth_image/256).astype('uint8')
    depth_gray=cv2.cvtColor(depth_gray,cv2.COLOR_GRAY2RGB)
    depth_gray_small=cv2.resize(depth_gray,None,fx=0.5,fy=0.5)
    if coloron:
        result_color=model_color(color_small)
        result_color_boxes=result_color[0].boxes.numpy()
        for i in range(0,len(result_color_boxes.cls)):
            cls=result_color_boxes.cls[i]
            xyxy=result_color_boxes.xyxy[i]
            cv2.rectangle(color_small,(int(xyxy[0]),int(xyxy[1])),(int(xyxy[2]),int(xyxy[3])),result_boxcolors[int(cls)])
            xy1_after=cv2.perspectiveTransform(np.array([[(xyxy[0]*2,xyxy[1]*2)]]),mat)
            xy2_after=cv2.perspectiveTransform(np.array([[(xyxy[2]*2,xyxy[3]*2)]]),mat)
            if cls==1:
                mx=(xy1_after[0][0][0]+xy2_after[0][0][0])/2        
                my=(xy1_after[0][0][1]+xy2_after[0][0][1])/2
                cv2.putText(canvas,"C",(int(mx),int(my)),cv2.FONT_HERSHEY_COMPLEX,2.0,(0,0,255),thickness=3)        
                # cv2.circle(canvas,(int(mx),int(my)),20,(0,0,200),thickness=-1)
            else:
                cv2.rectangle(canvas,(int(xy1_after[0][0][0]),int(xy1_after[0][0][1])),(int(xy2_after[0][0][0]),int(xy2_after[0][0][1])),(255,0,0),thickness=5)
    if depthon:
        result_depth=model_depth(depth_gray_small)
        result_depth_boxes=result_depth[0].boxes.numpy()
        
        for i in range(0,len(result_depth_boxes.cls)):
            cls=result_depth_boxes.cls[i]
            xyxy=result_depth_boxes.xyxy[i]
            cv2.rectangle(depth_small,(int(xyxy[0]),int(xyxy[1])),(int(xyxy[2]),int(xyxy[3])),result_boxcolors[int(cls)])
            xy1_after=cv2.perspectiveTransform(np.array([[(xyxy[0]*2,xyxy[1]*2)]]),mat)
            xy2_after=cv2.perspectiveTransform(np.array([[(xyxy[2]*2,xyxy[3]*2)]]),mat)
            if cls==1:
                mx=(xy1_after[0][0][0]+xy2_after[0][0][0])/2        
                my=(xy1_after[0][0][1]+xy2_after[0][0][1])/2
                cv2.putText(canvas," D",(int(mx),int(my)),cv2.FONT_HERSHEY_COMPLEX,2.0,(0,255,0),thickness=3)        
                # cv2.circle(canvas,(int(mx),int(my)),20,(0,0,200),thickness=-1)
            else:
                cv2.rectangle(canvas,(int(xy1_after[0][0][0]),int(xy1_after[0][0][1])),(int(xy2_after[0][0][0]),int(xy2_after[0][0][1])),(255,0,0),thickness=5)
    images = np.hstack((color_small, depth_small))

    # Show images
    cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
    cv2.imshow('RealSense', images)
    cv2.imshow('Projector',projectimg)
    cv2.imshow('Canvas',canvas)
    key=cv2.waitKey(1)
    if key==27:
        print('break!')
        break
    elif key==99:
        coloron=not coloron
    elif key==100:
        depthon=not depthon
    elif key==48:
        contentsimg[0]=cv2.imread('./contents/textbook0.png')        
    elif key==49:
        contentsimg[0]=cv2.imread('./contents/textbook1.png')        
    elif key==50:
        contentsimg[0]=cv2.imread('./contents/textbook2.png')        
    elif key==51:
        contentsimg[0]=cv2.imread('./contents/textbook3.png')        
    elif key==52:
        contentsimg[0]=cv2.imread('./contents/textbook4.png')        
    if coloron:
        print("Detection with color is running")
    else:
        print("Detection with color is off")
    if depthon:
        print("Detection with depth is running")
    else:
        print("Detection with depth is off")

    # print(contents_corners_after)
#stop streaming
pipeline.stop()
config.disable_all_streams()
cv2.destroyAllWindows()
print('finish!')
