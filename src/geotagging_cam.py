#Author:Siddharth Chawla
#Revision: v0
#About: This file calls read.py and geotagging.py which initializes the uart interface for the UBlox SAM-M8Q GPS sensor and embeds location in .jpg files 



import io 
from PIL import Image
import piexif
import read
import sys
import serial
import geotagging as gt
from camera import Camera
import cv2
import os

PATH = os.path.dirname(os.path.abspath(__file__))
geo_tagged_img_dir = "geoimages"

PATH = os.path.join(PATH, geo_tagged_img_dir)

if(not os.path.exists(PATH)): 
    os.makedirs(PATH)

image_width = 1280
image_height = 720
video_dev = 1

cam = Camera(image_height, image_width)
cam.cap = cv2.VideoCapture(video_dev)
if not cam.cap.isOpened():
    sys.exit(1)

frame = cam.capture_image()
frame = Image.fromarray(frame)



def main():
    cam.capture_image();
    ser= gt.initialize_uart(sys.argv[1])
    message = ""
    while('GNGGA' not in message):
        message = ser.readline()
        message=message.decode("utf-8",errors='ignore')
    gps_dict= gt.readgps(message)
    lat_dms,long_dms=gt.transform(gps_dict)
    exif_dict = gt.generate_exif_dict(gps_dict,lat_dms,long_dms)
    exif_bytes = piexif.dump(exif_dict)
    frame.save(os.path.join(PATH,"test.jpg"),exif = exif_bytes)


main()
