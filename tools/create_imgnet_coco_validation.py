#!/usr/bin/python3
#make validation data from imgnet/coco datasets
import os
import argparse
import subprocess

parser = argparse.ArgumentParser(description="Training set folder")
parser.add_argument('--imgnet_folder', nargs='?', default='.',
                    help='Folder name of your imgnet data')
parser.add_argument('--coco_folder', nargs='?', default='.',
                    help='Folder name of your coco data')
parser.add_argument('--val_folder', nargs='?', default='.',
                    help='Folder name of your validation data')

args = parser.parse_args()
imgnet_folder = args.imgnet_folder
coco_folder = args.coco_folder
val_folder = args.val_folder

#this one is easy, because each class has a folder
def imgnet_val_data():
	#walk through each folder
	#for each subfolder, set 10% of data to validation data
	for root, dirs, files in os.walk(imgnet_folder):
		#get number of files in root (excluding directories)
		num_files = len(files)
		num_val_files = num_files * .10
		cur_num_val_files = 0
		print("number files: ", num_files, num_val_files)		
		for name in files:
			idx = name.rfind('.')
			jpg_loc = root + '/' + name[:idx] + '.jpg'
			txt_loc = root + '/' + name[:idx] + '.txt'
			#go through files until we have enough validation files
			if cur_num_val_files > num_val_files:
				break
			#move the image and text files
			subprocess.call(["/bin/mv " + jpg_loc + " " + os.path.abspath(val_folder)], shell=True)
			subprocess.call(["/bin/mv " + txt_loc + " " + os.path.abspath(val_folder)], shell=True)
			cur_num_val_files = cur_num_val_files + 1

#this one is harder, because we need to read the objects to sort
#create a dictionary of class to # of validation data
#for each class, if we have > 30, then skip it
def coco_val_data():
	#get class info
	with open('dumping.names', 'r') as file:
		l = file.read().splitlines()
	#assign each key (class) the value 0 initially
	d = {k:v for k,v in zip(l,[0]*len(l))}

	#walk through each folder
	#for each subfolder, set 10% of data to validation data
	for root, dirs, files in os.walk(coco_folder):	
		#for coco, we will go through all images and check object
		#we will use first object until that dict is > 30
		for name in files:
			#check if its a text file
			idx = name.rfind('.')
			txt = name[idx:]
			if txt == ".txt":
				f = open(os.path.abspath(root + '/' + name))
				#open file, read first line
				for line in f:
					elements = line.split(' ')
					#print(elements[0])
					key = l[int(elements[0])]
					#print("key: ", key)
					#check next object, if there is one
					if d[key] > 30:
						continue
					#if that class has <= 30 objects, then copy the jpg/txt file to the validation data folder					
					else:
						f.close()
						jpg_loc = root + '/' + name[:idx] + '.jpg'
						txt_loc = root + '/' + name[:idx] + '.txt'
						d[key] = d[key] + 1
						subprocess.call(["/bin/mv " + jpg_loc + " " + os.path.abspath(val_folder)], shell=True)
						subprocess.call(["/bin/mv " + txt_loc + " " + os.path.abspath(val_folder)], shell=True)
						#don't analyze file after we mark is as validation
						break
	#quit()
	return d


imgnet_val_data()
#out_val_nums = coco_val_data()
#print(out_val_nums)



