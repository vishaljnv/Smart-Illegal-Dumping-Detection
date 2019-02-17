#!/usr/bin/python3
#Run this after doing the coco conversion to yolo
#Remove any annotation file with size 0
#Move relevant image files to new yolo folder
import argparse
import os
import subprocess
from pycocotools.coco import COCO

parser = argparse.ArgumentParser(description="Convert images annotations.")
parser.add_argument('--input_loc', nargs='?', default="./",
                    help='Input location')
parser.add_argument('--output_loc', nargs='?', default="./",
                    help='Output location')
parser.add_argument('--manifast_file', nargs='?', default="manifast.txt",
                    help='Output location')

args = parser.parse_args()
input_folder = args.input_loc
output_loc = args.output_loc
manifast_file = args.manifast_file
cwd = os.getcwd()

for root, dirs, files in os.walk(input_folder):
	#print(root)
	for name in files:
		orig_name = name
		#Train data name (e.g. trash_bags_193)
		idx = name.find('.')
		name = name[:idx]

		img_name = root + '/' + name  + '.jpg'
		txt_name = output_loc + '/' + name + '.txt'
		#check if txt is a real file, could be we don't have it
		if os.path.isfile(txt_name):
			stat = os.stat(txt_name)
			#if text file is empty, don't both copying the image
			if stat.st_size == 0:
				subprocess.call(["/bin/rm", txt_name])
				continue
			manifast = open(cwd + '/' + manifast_file)
			result = manifast.read().find(name)
			if result == -1:
				continue
			else:
				subprocess.call(["/bin/cp", img_name, output_loc])

