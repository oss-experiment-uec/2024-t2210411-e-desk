#!/usr/bin/env python3
# coding: utf-8
import cv2
import numpy as np
import argparse

# ArUcoのライブラリを導入
aruco = cv2.aruco

# 4x4のマーカ, IDは50までの辞書を使用
dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)

markpixel = 80
paperpixely = 1920
paperpixelx = 1080
offset = 10
cnt = 8

def generateArMarker(lenx=paperpixelx, leny=paperpixely):
    img = np.zeros((paperpixelx, paperpixely), dtype=np.uint8)
    img += 255
    ar_image0 = cv2.rotate(aruco.generateImageMarker(dictionary, 0, markpixel, 3), cv2.ROTATE_180)
    ar_image1 = cv2.rotate(aruco.generateImageMarker(dictionary, 1, markpixel, 3), cv2.ROTATE_90_COUNTERCLOCKWISE)
    ar_image2 = aruco.generateImageMarker(dictionary, 2, markpixel, 3)
    ar_image3 = cv2.rotate(aruco.generateImageMarker(dictionary, 3, markpixel, 3), cv2.ROTATE_90_CLOCKWISE)

    ar_image4 = cv2.rotate(aruco.generateImageMarker(dictionary, 4, markpixel, 3), cv2.ROTATE_90_CLOCKWISE)
    ar_image5 = cv2.rotate(aruco.generateImageMarker(dictionary, 5, markpixel, 3), cv2.ROTATE_180)
    ar_image6 = cv2.rotate(aruco.generateImageMarker(dictionary, 6, markpixel, 3), cv2.ROTATE_90_COUNTERCLOCKWISE)
    ar_image7 = aruco.generateImageMarker(dictionary, 7, markpixel, 3)
    img[offset:offset + markpixel, offset:offset + markpixel] = ar_image0
    img[offset:offset + markpixel, paperpixely-offset-markpixel:paperpixely-offset] = ar_image1
    img[paperpixelx-offset-markpixel:paperpixelx-offset, paperpixely-offset-markpixel:paperpixely-offset] = ar_image2
    img[paperpixelx-offset-markpixel:paperpixelx-offset, offset:offset + markpixel] = ar_image3

    img[offset + markpixel:offset + markpixel*2, offset + markpixel:offset + markpixel*2] = ar_image4
    img[offset + markpixel:offset + markpixel*2, leny-offset-markpixel*2:leny-offset-markpixel] = ar_image5
    img[lenx-offset-markpixel*2:lenx-offset-markpixel, leny-offset-markpixel*2:leny-offset-markpixel] = ar_image6
    img[lenx-offset-markpixel*2:lenx-offset-markpixel, offset + markpixel:offset + markpixel*2] = ar_image7
    rgb_img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    cv2.imwrite('VirtualDesk.png', rgb_img)

if __name__ == "__main__":
    parser=argparse.ArgumentParser(
        description="Generate the picture from VirtualCamera for e-desk"
    )
    parser.add_argument("--lenx", help="the length of x (in [200, 1080])", type=int)
    parser.add_argument("--leny", help="the length of y (in [200, 1920])", type=int)
    args=parser.parse_args()

    generateArMarker(args.lenx, args.leny)