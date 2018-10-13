from os import listdir
from os.path import isfile, join,expanduser
from PIL import Image
from datetime import *
from scipy.misc import imread
from gps import *
import os
import time
import argparse
import cv2
import numpy as np
import matplotlib as mp
import os, os.path
import shutil
import threading
begin_time = time.time()
import requests
import json
import datetime
import glob
import base64
import sys

sys.path.append(os.path.join('/home/nvidia/darknet/','python/')) #join darknet path to home to import 
import darknet as dn
import pdb

mp.use('Agg')

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

classifier_list = []
images=[]
classifier = []
path="/home/nvidia/Downloads/Raw_Images"
dstdir = "/home/nvidia/Downloads/Classified_Images"

data_to_send_dict = {}
images_list_file = []
camera_list = []
reg_station_id = ""
threads = []
labels_list = ['cart', 'electronics','furniture', 'mattress', 'sofa', 'trash_bags', 'trash']

windowName = "CameraDemo"

headers = {'Content-type': 'application/json'}
print("Testing connection")
url = "http://130.65.159.74/test"
data_to_send_dict = {"data":"test request"}
r = requests.post(url, data=json.dumps(data_to_send_dict), headers=headers)
print (r.content)

print("Registering with the server")
url = "http://130.65.159.74/register"
camera_list.append({"model":"Geo Vision GV-EDR4700-0F","type":"Action camera - 1440p","image_format":"JPEG","installation_position":"front-left"})
date_time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
desc = "This is a hotspot station, with "+str(len(camera_list))+" cameras "
data_to_send_dict ={"station_type":"hotspot","cameras":camera_list,"registered_time": date_time,"description": desc}
r = requests.post(url, data=json.dumps(data_to_send_dict), headers=headers)

temp_stat = json.loads(r.content)

reg_station_id = temp_stat["station_id"]

print (r.content)

print("Connecting to the server")
url = "http://130.65.159.74/connect"
date_of_connection = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

'''location_hotspot1 = geocoder.google("Fremont,CA")
print(location_hotspot1)
print(location_hotspot1.latlng)
lat_lng = str((location_hotspot1.latlng)[0]) + ", " + str((location_hotspot1.latlng)[1])
#print (lat_lng)
#print (date_of_connection)
#lng = (location_hotspot.latlng)[1]
'''

gpsd = gps(mode=WATCH_ENABLE)
lat_lng = str(gpsd.fix.latitude)+","+ str(gpsd.fix.longitude)
data_to_send_dict = {"station_id": reg_station_id,"connection_time" : date_of_connection ,"location": lat_lng}
r = requests.post(url, data=json.dumps(data_to_send_dict), headers=headers)
print (r.content)

#Load config files
dn.set_gpu(0)
home = expanduser("~")
net = dn.load_net(bytes(home+ "/darknet/yolo-obj.cfg"), bytes(home + "/darknet/yolo-obj_40000.weights"), 0)
meta = dn.load_meta(bytes(home + "/darknet/obj.data"))
if not os.path.exists(home+'/Downloads/Raw_Images'):
	os.makedirs(home+'/Downloads/Raw_Images');
if not os.path.exists(home+'/Downloads/Classified_Images'):
	os.makedirs(home+'/Downloads/Classified_Images');

def main():
	while True:
		start = time.time()
		print (datetime.datetime.now())
		mydir_tegra = os.path.join(home + '/Downloads/Raw_Images/',(datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')))
		mydir_illegal = os.path.join(home + '/Downloads/Classified_Images/',datetime.datetime.now().strftime('%Y-%m-%d_%H-%M'))
		os.makedirs(mydir_tegra)
		os.makedirs(mydir_illegal)
		mydir_tegra += '/'
		mydir_illegal += '/'
		tegra_cam(mydir_tegra)	
		test_time = time.time()
		testing_illegal(mydir_tegra, mydir_illegal)
		latency_detect = time.time() - test_time
		http_client()
		latency_total = time.time() - begin_time 
		latency_once = time.time() - start
		print ("Total time from load to send alerts:"+latency_total+" Total time from capture to send alerts:"+latency_once+" Total time for detection:"+latency_detect)
		time.sleep(60)
		mydir_tegra = ""
		mydir_illegal = ""
		images = []
		images_list_file = []
	
def tegra_cam(mydir_tegra):
    count = 1
    file_loc = mydir_tegra + "test_image"
    print("OpenCV version: {}".format(cv2.__version__))
    use_rtsp = 0
    use_usb = 1
    image_width = 1280
    image_height = 720
    rtsp_uri = None
    rtsp_latency = 200
    video_dev = 0

    if use_rtsp:
        cap = open_cam_rtsp(rtsp_uri, image_width, image_height, rtsp_latency)
    elif use_usb:
        cap = open_cam_usb(video_dev, image_width, image_height)
    else: # by default, use the Jetson onboard camera
        cap = open_cam_onboard(image_width, image_height)

    if not cap.isOpened():
        sys.exit("Failed to open camera!")

    open_window(windowName, image_width, image_height)
    read_cam(windowName, cap)
    start_time = time.time()
    while(time.time() - start_time < 1):
        file_name = file_loc + str(count)+".png"
        ret, frame = cap.read()
        cv2.imwrite(file_name,frame)
        count += 1
    cap.release()
    cv2.destroyAllWindows()


def open_cam_rtsp(uri, width, height, latency):
    gst_str = ("rtspsrc location={} latency={} ! rtph264depay ! h264parse ! omxh264dec ! "
               "nvvidconv ! video/x-raw, width=(int){}, height=(int){}, format=(string)BGRx ! "
               "videoconvert ! appsink").format(uri, latency, width, height)
    return cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)

def open_cam_usb(dev, width, height):
    # We want to set width and height here, otherwise we could just do:
    #     return cv2.VideoCapture(dev)
    gst_str = ("v4l2src device=/dev/video{} ! "
               "video/x-raw, width=(int){}, height=(int){}, format=(string)RGB ! "
               "videorate !"
               "video/x-raw,framerate=1/1 !"
               "videoconvert ! appsink").format(dev, width, height)
    return cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)

def open_cam_onboard(width, height):
    # On versions of L4T previous to L4T 28.1, flip-method=2
    # Use Jetson onboard camera
    gst_str = ("nvcamerasrc ! "
               "video/x-raw(memory:NVMM), width=(int)2592, height=(int)1458, format=(string)I420, framerate=(fraction)30/1 ! "
               "nvvidconv ! video/x-raw, width=(int){}, height=(int){}, format=(string)BGRx ! "
               "videoconvert ! appsink").format(width, height)
    return cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)

def open_window(windowName, width, height):
    cv2.namedWindow(windowName, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(windowName, width, height)
    cv2.moveWindow(windowName, 0, 0)
    cv2.setWindowTitle(windowName, "Camera Demo for Jetson TX2/TX1")

def read_cam(windowName, cap):
    showHelp = True
    showFullScreen = False
    helpText = "'Esc' to Quit, 'H' to Toggle Help, 'F' to Toggle Fullscreen"
    font = cv2.FONT_HERSHEY_PLAIN
    start_time = time.time()
    while (time.time() - start_time < 1):
        if cv2.getWindowProperty(windowName, 0) < 0: # Check to see if the user closed the window
            # This will fail if the user closed the window; Nasties get printed to the console
            break;
        ret_val, displayBuf = cap.read();
        if showHelp == True:
            cv2.putText(displayBuf, helpText, (11,20), font, 1.0, (32,32,32), 4, cv2.LINE_AA)
            cv2.putText(displayBuf, helpText, (10,20), font, 1.0, (240,240,240), 1, cv2.LINE_AA)
        cv2.imshow(windowName, displayBuf)
        key = cv2.waitKey(10)
        if key == 27: # ESC key: quit program
            break
        elif key == ord('H') or key == ord('h'): # toggle help message
            showHelp = not showHelp
        elif key == ord('F') or key == ord('f'): # toggle fullscreen
            showFullScreen = not showFullScreen
            if showFullScreen == True: 
                cv2.setWindowProperty(windowName, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            else:
                cv2.setWindowProperty(windowName, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL) 


def testing_illegal(mydir_tegra, mydir_illegal):

	#Raw folder path
	folder_raw = mydir_tegra
	print (mydir_tegra)
	files = os.listdir(folder_raw)
	print (files)

	#Classified folder path
	folder_classified = mydir_illegal
	count = 0
	font = cv2.FONT_HERSHEY_SIMPLEX

	chart_colors = [(204,102,51),(18,557,220),(0,153,255),(24,150,16),(175,175,246),(172,62,59),(198,153,0)]
	#Perform detection for every image in the files list
	#images = []
	for f in files:
		if f.endswith(".jpg") or f.endswith(".jpeg") or f.endswith(".png"):
			print (f)
			classifier = []
			#file1.write(f+" ")
			image_cv2 = cv2.imread(os.path.join(folder_raw,f),cv2.IMREAD_COLOR)
			image_path = bytes(os.path.join(folder_raw, f).encode("utf-8"))
			r = dn.detect(net, meta, image_path)
			print (r)
			cnt = 0
			if r != []:
				while cnt < len(r):
					name = r[cnt][0]
					if name in labels_list:
						i = labels_list.index(name)
					predict = r[cnt][1]
					#print (name+":"+str(predict))
					classifier.append(name)

					x = r[cnt][2][0]
					y = r[cnt][2][1]
					w = r[cnt][2][2]
					z = r[cnt][2][3]

					x_max = int(round((2*x+w)/2))
					x_min = int(round((2*x-w)/2))
					y_min = int(round((2*y-z)/2))
					y_max = int(round((2*y+z)/2))
					print (x_min, y_min, x_max, y_max)
					pixel_list = [ x_min, y_min, x_max, y_max]
					neg_index = [pixel_list.index(val) for val in pixel_list if val < 0]
					cv2.rectangle(image_cv2,(x_min,y_min),(x_max,y_max),(chart_colors[i]), 2)
					if neg_index == []:
						cv2.rectangle(image_cv2,(x_min,y_min-24), (x_min+10*len(name),y_min),chart_colors[i],-1)
						cv2.putText(image_cv2,name,(x_min,y_min-12), font, 0.5,(0,0,0),1,cv2.LINE_AA)
					else:
						if (y_min < 0 and x_min > 0):
								cv2.rectangle(image_cv2,(x_min,0), (x_min+10*len(name),24),chart_colors[i],-1)
								cv2.putText(image_cv2,name,(x_min,12), font, 0.5,(0,0,0),1,cv2.LINE_AA)
						elif (x_min < 0 and y_min > 0):
								cv2.rectangle(image_cv2,(0,y_min-24), (10*len(name),y_min),chart_colors[i],-1)
								cv2.putText(image_cv2,name,(0,y_min-12), font, 0.5,(0,0,0),1,cv2.LINE_AA)
						elif (x_min < 0 and y_min < 0):
								cv2.rectangle(image_cv2,(0,24), (10*len(name),48),chart_colors[i],-1)
								cv2.putText(image_cv2,name,(0,12), font, 0.5,(0,0,0),1,cv2.LINE_AA)
					#cv2.imshow('image',image_cv2)
					#cropped = image.crop((x_min, y_min+20, x_max, y_max))
					cnt+=1
				classifier_list.append(" ".join(set(classifier)))
				count += 1
				saving_path = folder_classified+ name +"_"+ str(count) + ".jpg"
				print (saving_path)
				images.append(saving_path)
				#file1.write(name+",")
				cv2.imwrite(saving_path,image_cv2)
				cv2.destroyAllWindows()
			#file1.write("\n")
#file1.close()

def http_client():
	print (images)
	try:		
		#if (images != []):
			print("Sending alert")
			url = "http://130.65.159.74/alerting"
			date_of_connection = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

			#lat_lng = str((location_hotspot1.latlng)[0]) + ", " + str((location_hotspot1.latlng)[1])
			#print (lat_lng)
			#print (date_of_connection)
			#print (images)
			for file in images:
				print (file)
				#print ("In files")
				with open(file,"rb") as image_file:
					#print ("Inside open")
					encoded_string = "data:image/jpeg;base64," + base64.b64encode(image_file.read())
					images_list_file.append(encoded_string)
					encoded_string = ""
					#print (encoded_string)
			#print (len(images_list_file))
			#print (images_list_file)
			#lng = (location_hotspot.latlng)[1]
				#for s in labels_list:
					#if s in file:
						#print s
						#print file
						#classifier.append(s)
			#classifier.append(s for s in labels_list if s in file)
			print (classifier)
			data_to_send_dict = {"station_id": reg_station_id,"alerting_type":"IllegalDumpingAlert","classifier": classifier_list,"alerting_time" : date_of_connection ,"location": lat_lng,"description":"This is an alert from a 			truck at San Jose","images":images_list_file}
			#print (data_to_send_dict)
			r = requests.post(url, data=json.dumps(data_to_send_dict), headers=headers)
			print (r.content)
		#else:
			#print ("No illegal dumping detected. Not sending alert")
	except KeyboardInterrupt:
		print ('Completed')

if __name__ == "__main__":
	main()
