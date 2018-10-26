#!/usr/bin/python
import time
begin_time = time.time()
import gps
import os
import cv2
#import matplotlib as mp
import requests
import json
import datetime
import base64
import sys
from camera import Camera

sys.path.append(os.path.join('/home/nvidia/darknet/','python/')) #join darknet path to home to import 
import darknet as dn

mp.use('Agg')
client = HttpClient("130.65.159.74")

use_rtsp = 0
use_usb = 1
image_width = 1280
image_height = 720
rtsp_uri = None
rtsp_latency = 200
video_dev = 0

global cam
cam = None

classifier_list = []
images = []
classifier = []
path = "/home/nvidia/Downloads/Raw_Images"
dstdir = "/home/nvidia/Downloads/Classified_Images"

images_list_file = []
camera_list = []
labels_list = ['cart', 'electronics','furniture', 'mattress', 'sofa', 'trash_bags', 'trash']

windowName = "CameraDemo"

gpsd = gps.gps(mode=WATCH_ENABLE)
cur_location = str(gpsd.fix.latitude)+","+ str(gpsd.fix.longitude)

if not client.is_server_up():
    print "Server is down!"

if not client.register_with_server():
    print "Could not register with server!"

if not client.connect_to_server(cur_location):
    print "Could not connect to server!"


#Load config files
dn.set_gpu(0)
home = os.expanduser("~")
net = dn.load_net(bytes(home+ "/darknet/yolo-obj.cfg"), bytes(home + "/darknet/yolo-obj_40000.weights"), 0)
meta = dn.load_meta(bytes(home + "/darknet/obj.data"))
if not os.path.exists(home+'/Downloads/Raw_Images'):
	os.makedirs(home+'/Downloads/Raw_Images');
if not os.path.exists(home+'/Downloads/Classified_Images'):
	os.makedirs(home+'/Downloads/Classified_Images');

def open_cam():	
    global cam
    cam = Camera(image_height, image_width)
    if use_rtsp:
        cam.open_cam_rtsp(rtsp_uri, rtsp_latency)
    elif use_usb:
        cam.open_cam_usb(video_dev)
    else: # by default, use the Jetson onboard camera
        cam.open_cam_onboard()


def take_pictures(mydir_tegra):
    count = 1
    file_loc = mydir_tegra + "test_image"
    print("OpenCV version: {}".format(cv2.__version__))

    start_time = time.time()
    while(time.time() - start_time < 1):
        file_name = file_loc + str(count)+".png"
        cam.capture_image(file_name)
        count += 1


open_cam()


def main():
	while True:
                location  = "here, there"
		start = time.time()
		print (datetime.datetime.now())
		mydir_tegra = os.path.join(home + '/Downloads/Raw_Images/',(datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')))
		mydir_illegal = os.path.join(home + '/Downloads/Classified_Images/',datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
		os.makedirs(mydir_tegra)
		os.makedirs(mydir_illegal)
		mydir_tegra += '/'
		mydir_illegal += '/'
		cam_time = time.time()
		take_pictures(mydir_tegra)
		print "Capture time:", time.time() - cam_time
		test_time = time.time()
		testing_illegal(mydir_tegra, mydir_illegal)
		latency_detect = time.time() - test_time
		client.send_detection_results(images, classifier_list, location)
		latency_total = time.time() - begin_time 
		latency_once = time.time() - start
		print ("Total time from load to send alerts:"+str(latency_total)+" Total time from capture to send alerts:"+str(latency_once)+" Total time for detection:"+str(latency_detect))
                print "\n\n\n\n"
		time.sleep(10)
		mydir_tegra = ""
		mydir_illegal = ""
		images = []
		images_list_file = []


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


if __name__ == "__main__":
	main()
