#!/usr/bin/python3
#clean previous team's data for new class list
import argparse
import os
import subprocess
from pycocotools.coco import COCO


parser = argparse.ArgumentParser(description="Convert images annotations.")
parser.add_argument('--input_loc', nargs='?', default="./",
                    help='Input location')
parser.add_argument('--output_loc', nargs='?', default="./",
                    help='Output location')
parser.add_argument('--is_coco', nargs='?', default=0,
                    help='Output location', type=int)
parser.add_argument('--manifast_file', nargs='?', default="manifast.txt",
                    help='Output location')
parser.add_argument('--coco_imgs', nargs='?', default="val2014",
                    help='coco img location')
parser.add_argument('--names_loc', nargs='?', default="../tools/",
                    help='names files location')
args = parser.parse_args()
input_folder = args.input_loc
output_loc = args.output_loc
is_coco = args.is_coco
#list of all the images we converted
manifast_file = args.manifast_file
coco_imgs = args.coco_imgs
names_loc = args.names_loc
cwd = os.getcwd()


#convert existing illegal dumping data to new class list
prev_class_names = names_loc + "obj.names"
new_class_names = names_loc + "dumping.names"

#coco class names
catNms=['person','backpack','bottle','chair', 'couch','dining table','tv','microwave oven','toaster']

def check_jpg_and_txt(in_folder,name,is_coco):
	global manifast_file
	if is_coco == 0:
		#print('check: ' + name + '_' + num)
		new_name = in_folder + '/' + name
		#print(new_name)
		if os.path.isfile(new_name + '.jpg') and os.path.isfile(new_name + '.txt'):
			return 1
		else:
			return 0
	else:
	#for coco, check if the .jpg file name is in the manifast file
		print(name)
		manifast = open(cwd + '/' + manifast_file)
		result = manifast.read().find(name)
		if result == -1:
			return 0
		else:
			return 1

#remove annotations with electronics, furniture, trash (1, 2, 5)
def convert_file(in_folder,name,out_loc):
	new_name = in_folder + '/' + name
	new_file = out_loc + '/' + name + '.txt'
	#print(new_name)
	#get object class from .txt file
	txt = open(new_name + '.txt', "r")
	new_txt = open(new_file, "w")
	for line in txt:
		elements = line.split(" ")
		name_id = elements[0]
		#get value as an int, not str
		name_id = int(name_id)
		#print(name_id)
		if ((name_id == 1) or (name_id == 2) or (name_id == 5)):
			continue
		else:
			new_txt.write(line)
	#print("leave for loop")
	txt.close()
	new_txt.close()
	#if new file is empty, delete it
	stat = os.stat(new_file)
	#print("size: ", stat.st_size)
	if stat.st_size == 0:
		subprocess.call(["/bin/rm", new_file])
	#if new file isn't empty, copy the image too
	else:
		subprocess.call(["/bin/cp", new_name + ".jpg", out_loc])


def get_list_dumping_ids():
	dumping_ids = open(new_class_names)
	illegal_ids = []
	for line in dumping_ids:
		line = line.rstrip()
		illegal_ids.append(line)

	print(illegal_ids)
	return illegal_ids

#class ID of yolo file is going to be based on our catNms
#e.g. person class will be listed as "0"
#need to conver this from catNms index to dumping index
def compare_coco_index(coco_id, illegal_ids):
	print("coco id: ", coco_id)
	#get conversion mapping from catNms to illegal ids
	cat_name = catNms[coco_id]
	for i in range(0,len(illegal_ids)):
		#print("cat_name: ", cat_name, "ill id: ", illegal_ids[i])
		if(cat_name == illegal_ids[i]):
			#print("match, id: ", illegal_ids[i])
			break
	#quit()
	return i
		

#convert coco file classes to our class list
#get index of class in coco
#get index of class in our file
#if index of class in coco is != our class, change it
def convert_file_coco(in_folder,name,out_loc,illegal_ids):
	new_name = in_folder + '/' + name
	img_name = coco_imgs + '/' + name + '.jpg'
	new_file = out_loc + '/' + name + '.txt'
	#print(new_name)
	#get object class from .txt file
	txt = open(new_name + '.txt', "r")
	new_txt = open(new_file, "w")
	#ignore any object that is not relevant for our data
	for line in txt:
		elements = line.split(" ")
		name_id = elements[0]
		#get value as an int, not str
		name_id = int(name_id)
		#print(name_id)
		new_id = compare_coco_index(name_id, illegal_ids)
		#reconstruct new line based on new id
		print(line)
		elements[0] = str(new_id)
		new_line = ""
		for e in range(0, len(elements)):
			new_line = new_line + ' ' + elements[e]
		new_line = new_line[1:]
		print(new_line)
		new_txt.write(line)
	#print("leave for loop")
	txt.close()
	new_txt.close()
	#if new file is empty, delete it
	stat = os.stat(new_file)
	print("size: ", stat.st_size)
	print("new file: ", new_file)
	print("img name: ", img_name)
	quit()
	if stat.st_size == 0:
		subprocess.call(["/bin/rm", new_file])
	#if new file isn't empty, copy the image too
	else:
		subprocess.call(["/bin/cp", img_name, out_loc])

def convert_annotations(in_folder, out_folder, illegal_ids):
	#new_classes = open(new_class_names, "r")
	for root, dirs, files in os.walk(in_folder):
		#print(root)
		for name in files:
			orig_name = name
			#Train data name (e.g. trash_bags_193)
			idx = name.find('.')
			name = name[:idx]

			#only need to convert txt files
			if(orig_name[idx+1:] == 'jpg'):
				continue
			#if there is an image and labeled data, then convert labels
			if(check_jpg_and_txt(root,name,is_coco) == 1):
				if is_coco:
					convert_file_coco(root,name,out_folder,illegal_ids)
				else:
					convert_file(root,name,out_folder)
				#train_f.write(os.path.abspath(root + '/' + orig_name) + '\n')

illegal_ids = get_list_dumping_ids()
convert_annotations(input_folder, output_loc, illegal_ids)
