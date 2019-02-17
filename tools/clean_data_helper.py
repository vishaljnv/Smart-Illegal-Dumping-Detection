#!/usr/bin/python3
"""
" Run this tool to easily verify good/bad data.
"
"""

import argparse
import matplotlib.pyplot as plt
import os
import skimage.io as io
import subprocess
import cv2
import readchar

parser = argparse.ArgumentParser(description="Clean data image location.")
parser.add_argument('--input_loc', nargs='?', default="./",
                    help='Input location')
parser.add_argument('--names_loc', nargs='?', default="./",
                    help='class names location')
parser.add_argument('--output_loc', nargs='?', default="./",
                    help='Output location')
args = parser.parse_args()
input_folder = args.input_loc
names_loc = args.names_loc
output_folder = args.output_loc


if os.path.isdir(output_folder) != True:
    os.mkdir(output_folder)

#Go through the files
#Open the image and txt files in different sides of the screen
#Give a check mark and X mark GUI
#If good, check accepts, if bad X will delete the jpg and txt file
#Prompt the user with things to check for
#	E.g. Does this image have (classes = ???)

def check_jpg_and_txt(in_folder,name):
	new_name = in_folder + '/' + name
	if os.path.isfile(new_name + '.jpg') and os.path.isfile(new_name + '.txt'):
		return 1
	else:
		return 0

def get_bounding_boxes(x_arr,y_arr,w_arr,h_arr,img):
	height, width, channels = img.shape
	new_x_arr = []
	new_y_arr = []
	new_h_arr = []
	new_w_arr = []
	for i in range(0, len(x_arr)):
		centerX = int(float(x_arr[i]) * width)
		centerY = int(float(y_arr[i]) * height)
		box_w = int(float(w_arr[i]) * width)
		box_h = int(float(h_arr[i]) * width)
		new_x_arr.append(int(centerX - (box_w / 2)))
		new_y_arr.append(int(centerY - (box_h / 2)))
		new_w_arr.append(int(box_w))
		new_h_arr.append(int(box_h))
	return new_x_arr, new_y_arr, new_h_arr, new_w_arr

def print_class_info(file):
	names = open(names_loc + '/dumping.names')
	annotations = open(file)
	class_idx = 0
	class_nums = []
	#Arrays to store all the bounding box values
	x_arr= []
	y_arr = []
	w_arr = []
	h_arr = []
	#First get all the classes from the annotation file
	for line in annotations:
		class_idx = line.find(" ")
		class_num = line[:class_idx]
		class_nums.append(class_num)

		#Get coordinates to draw bounding boxes later
		new_line = line[class_idx+1:]
		space_idx = new_line.find(" ")
		x = new_line[:space_idx]
		x_arr.append(x)
		new_line = new_line[space_idx+1:]
		space_idx = new_line.find(" ")
		y = new_line[:space_idx]
		y_arr.append(y)
		new_line = new_line[space_idx+1:]
		space_idx = new_line.find(" ")
		w = new_line[:space_idx]
		w_arr.append(w)
		new_line = new_line[space_idx+1:]
		space_idx = new_line.find(" ")
		h = new_line[:space_idx]
		h_arr.append(h)

	#Only get unique numbers
	class_set = set(class_nums)
	print("Does this image contain: ")
	class_idx = 0
	#Then print all of the class names we are looking for
	for class_name in names:
		if str(class_idx) in class_set:
			print(class_name)
		class_idx = class_idx + 1
	names.close()
	return x_arr,y_arr,w_arr,h_arr,class_nums

def get_class_name(class_num):
	names = open(names_loc + '/dumping.names')	
	class_idx = 0
	for class_name in names:
		if int(class_num) == class_idx:
			return class_name
		class_idx = class_idx + 1
	names.close()

#Reference: https://github.com/matplotlib/matplotlib/issues/830/
def quit_figure(event):
	#There's probably a better way to do this, but its fine for now
	global input_folder
	global output_folder
	global img_name
	global orig_name

	if event.key == 'y':
		subprocess.call(["/bin/mv", img_file, output_folder])
		subprocess.call(["/bin/mv", txt_file, output_folder])
		plt.close(event.canvas.figure)
	#If we don't find the correct data, remove the image & txt file
	elif event.key == 'n':
		subprocess.call(["/bin/rm", img_file])
		subprocess.call(["/bin/rm", txt_file])
		plt.close(event.canvas.figure)
	elif event.key == '.' or event.key == 'q':
		plt.close(event.canvas.figure)
		quit()

cid = plt.gcf().canvas.mpl_connect('key_press_event', quit_figure)

for root, dirs, files in os.walk(input_folder):
	for name in files:
		cur_dir = root
		orig_name = name
		#Train data name (e.g. trash_bags_193)
		idx = name.find('.')
		name = name[:idx]

		#Only go by txt files
		if(orig_name[idx+1:] == 'jpg'):
			continue
		#if there is an image and labeled data, then show the data
		if(check_jpg_and_txt(root,name) == 1):
			img_name = orig_name[:idx] + '.jpg'
			txt_file = cur_dir + '/' + orig_name
			img_file = cur_dir + '/' + img_name
			#Print the classes found for the image
			#Also get bounding box info
			x_arr, y_arr, w_arr, h_arr,class_nums = print_class_info(txt_file)
			#Use matplotlib for showing image
			#I = io.imread(input_folder + '/' + img_name)
			I = cv2.imread(img_file, cv2.IMREAD_COLOR)
			#Re-load image so it displays correctly with matplotlib (RGB format)
			b,g,r = cv2.split(I)
			img = cv2.merge([r,g,b])    
			x_arr, y_arr, w_arr, h_arr = get_bounding_boxes(x_arr,y_arr,w_arr,h_arr,img)

			for i in range(0,len(x_arr)):
				color = 122
				cv2.rectangle(img, (x_arr[i], y_arr[i]), (x_arr[i] + w_arr[i], y_arr[i] + h_arr[i]), color, 3)
				text = get_class_name(class_nums[i])
				cv2.putText(img, text, (int(x_arr[i]), int(y_arr[i]) - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 10, 2)
			plt.imshow(img)
			#Check for what key the user presses while image is displayed
			plt.gcf().canvas.mpl_connect('key_press_event', quit_figure)
			plt.show()
			#while True:
				#key = input('y/n/.:')  
				#key = readchar.readkey()
				#Move good images to a clean folder
				#if key == 'y':
				#	subprocess.call(["/bin/mv", input_folder + '/' + img_name, output_folder])
				#	subprocess.call(["/bin/mv", input_folder + '/' + orig_name, output_folder])
				#	break
				#If we don't find the correct data, remove the image & txt file
				#elif key == 'n':
				#	subprocess.call(["/bin/rm", input_folder + '/' + img_name])
				#	subprocess.call(["/bin/rm", input_folder + '/' + orig_name])
				#	break
				#elif key == '.':
				#	quit()
			#plt.close()
		


