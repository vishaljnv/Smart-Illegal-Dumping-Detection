#!/usr/bin/python3
#Find any non-jpg files, and convert them to jpg
import os
import argparse
import imghdr
from PIL import Image
import subprocess

parser = argparse.ArgumentParser(description="Training set folder")
parser.add_argument('--in_folder', nargs='?', default='.',
                    help='Folder name of your train data')
args = parser.parse_args()
in_folder = args.in_folder

for root, dirs, files in os.walk(in_folder):
	#go through all images called "jpg" in the directory
	for name in files:
		subprocess.call(['chmod', '0666', root + '/' + name])
		idx = name.rfind('.')
		is_jpg = name[idx:]
		#print(is_jpg)
		#quit()
		if is_jpg == '.jpg':
			#check if actually not a jpg
			img_type = imghdr.what(root + '/' + name)
			#print(img_type)
			#I found out that if it is png, probably the file is just garbage
			#so delete all of these rogue files 
			if img_type == 'png' or img_type == None:
				#print("converting image: ", root + '/' + name)
				#im = Image.open(root + '/' + name)
				#rgb_im = im.convert('RGB')
				#test = rgb_im.save(root + '/' + name, format="JPEG")
			#if img_type == None:
				#if image is none, just delete is and its txt file cousin
				idx = name.rfind('.')
				#yes i know this is lazy :(
				name = name[:idx]
				jpg_name = root + '/' + name + '.jpg'
				txt_name = root + '/' + name + '.txt'
				subprocess.call(["/bin/rm", jpg_name])
				subprocess.call(["/bin/rm", txt_name])
			#quit()
