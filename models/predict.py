from ultralytics import YOLO
import cv2
model=YOLO("best_8m.pt")
result=model(4,show=True,save=True,device='cpu')
