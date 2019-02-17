#!/usr/bin/python
from __future__ import print_function
import os
import argparse
import subprocess

parser = argparse.ArgumentParser(description="Training set folder")
parser.add_argument('--in_folder', nargs='?', default='.',
                    help='Folder name of your train data')
parser.add_argument('--test_folder', nargs='?', default='.',
                    help='Folder name of your test data')

def check_jpg_and_txt(in_folder,name):
	#print('check: ' + name + '_' + num)
	new_name = in_folder + '/' + name
	#print(new_name)
	if os.path.isfile(new_name + '.jpg') and os.path.isfile(new_name + '.txt'):
		return 1
	else:
		return 0

def create_train(in_folder):
	train_f = open("train.txt", "a+")
	for root, dirs, files in os.walk(in_folder):
		#print(root)
		for name in files:
			orig_name = name
			#Train data name (e.g. trash_bags_193)		
			idx = name.find('.')
			name = name[:idx]

			#only add jpg files to train file
			if(orig_name[idx+1:] == 'txt'):
				continue
			#if there is an image and labeled data, add to train.txt
			if(check_jpg_and_txt(root,name) == 1):
				train_f.write(os.path.abspath(root + '/' + orig_name) + '\n')

	train_f.close()

def create_test(test_folder):
	test_f = open("test.txt", "a+")
	for root, dirs, files in os.walk(test_folder):
		print(root)
		for name in files:
			orig_name = name
			#Train data name (e.g. trash_bags_193)		
			idx = name.find('.')
			name = name[:idx]

			#only add jpg files to train file
			if(orig_name[idx+1:] == 'txt'):
				continue
			#if there is an image and labeled data, add to train.txt
			if(check_jpg_and_txt(root,name) == 1):
				test_f.write(os.path.abspath(root + '/' + orig_name) + '\n')

	test_f.close()

#Glue logic
def main():
    	#subprocess.call(["/bin/rm", 'train.txt'])
    	#subprocess.call(["/bin/rm", 'test.txt'])
        args = parser.parse_args()
        in_folder = args.in_folder
        test_folder = args.test_folder

        create_train(in_folder)
        if test_folder != '.': 
	     create_test(test_folder)

#Main function called here
main()
