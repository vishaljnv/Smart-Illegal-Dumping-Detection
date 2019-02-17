#!/usr/bin/python3
#Get all the imagenet related data
#Get the bounding boxes for the imagenet data
#convert the bounding boxes to yolo format
#reference: https://www.pyimagesearch.com/2015/03/02/convert-url-to-image-with-python-and-opencv/

import urllib.request
import matplotlib
import skimage.io as io
import matplotlib.pyplot as plt
import numpy
import requests
import os
import subprocess
import glob
import time
import argparse

from YoloFormat import VOC, YOLO

parser = argparse.ArgumentParser(description="Coco data conversion")
parser.add_argument('--names_loc', nargs='?', default="./",
                    help='names of classes file')
args = parser.parse_args()
names_loc = args.names_loc

cwd = os.getcwd()
imgnet_classes = ["tire", "broom", "computer", "keyboard", "grill", "vacuum",
                    "pillow", "cabinet", "stool", "basket", "barrell",
                    "stroller", "bucket", "mats", "carpet", "box", "lightbulb",
                    "battery", "toy"]
#Imagenet uses WNID to identify the class
imgnet_wnid = "n02971167"
imgnet_wnid_arr = ["n02971167", "n02906734", "n03082979", "n03614007", "n03459591",
                    "n04517823", "n03938244", "n02933112", "n04326896", "n02801938",
                    "n02795169", "n02766534", "n02909870", "n03727946", "n04118021",
                    "n02883344", "n03665924", "n02810471", "n04461879"]

imgnet_annotations = cwd + "/" + "imgnet_annotations"
imgnet_images = cwd + "/" + "imgnet_images"
imgnet_grouped = cwd + "/" + "imgnet_grouped"
imgnet_yolo_format = cwd + "/" + "imgnet_yolo_format"
#Location to save annotations:
if os.path.isdir(imgnet_annotations) != True:
    os.mkdir(imgnet_annotations)
#Location to save images:
if os.path.isdir(imgnet_images) != True:
    os.mkdir(imgnet_images)
if os.path.isdir(imgnet_grouped) != True:
    os.mkdir(imgnet_grouped)
if os.path.isdir(imgnet_yolo_format) != True:
    os.mkdir(imgnet_yolo_format)

io.use_plugin('pil')

def do_request(html_page):
    attempts = 3
    while attempts > 0:
        try:
            response = requests.get(html_page, timeout=0.3)
            return response
        except:
            time.sleep(1)
            attempts = attempts - 1
            continue

def get_imgs(imgnet_wnid):
    url = 'http://www.image-net.org/api/text/imagenet.synset.geturls?wnid=' + imgnet_wnid
    print(url)

    #Get list of URLs
    response = urllib.request.urlopen(url)
    data = response.read()
    text = data.decode('utf-8')
    #print(text)
    #quit()

    #Create list of all the URLs provided
    elements = text.split("\n")
    #Get all imgs, save to folder

    #Create a place to save all the downloaded images
    if os.path.isdir(imgnet_images + '/' + imgnet_wnid) != True:
        os.mkdir(imgnet_images + '/' + imgnet_wnid)

    #Get all the images
    for i in range(0, len(elements)):
        img = elements[i]
        #print(str(img))
        #Save img title from last / to .jpg
        #TBD - if img is png, convert it to jpg first
        idx = img.rfind('/')
        img_title = img[idx+1:]
        idx = img_title.rfind('.')
        img_title = img_title[:idx]
        #print(img_title)
        #quit()
        #if we already have the file, continue
        if os.path.isfile(imgnet_images + '/' + imgnet_wnid + '/' + img_title + '.jpg'):
                continue

        #time.sleep(1)
	#if this fails, try using requester
        #try:
        #        img2 = io.imread(str(img))
                #print(imgnet_images + '/' + imgnet_wnid + '/' + img_title)
                #quit()
                #Save the image to a local file
        #        io.imsave(imgnet_images + '/' + imgnet_wnid + '/' + img_title + '.jpg',img2)
        #except:
        try:
             #print("Trying with requests API...")
             #r = requests.get(str(img), timeout=0.3)
             r = do_request(str(img))
             with open(imgnet_images + '/' + imgnet_wnid + '/' + img_title + '.jpg', "wb") as code:
                   code.write(r.content)
                   print('+')
        except: #if this doesn't work, just give up
             print('*')
             continue
        #Optionally show the image
        #plt.axis('off')
        #plt.imshow(img2)
        #print(".")
        #plt.show()
        #quit()

def get_bounding_boxes(imgnet_wnid):
    #Get list of all bounding boxes available
    bounding_box_list = 'http://www.image-net.org/api/text/imagenet.bbox.obtain_synset_list'

    #Get bounding box for url
    tar_name = imgnet_wnid + '.tar'
    bounding_box = 'http://www.image-net.org/api/download/imagenet.bbox.synset?wnid=' + imgnet_wnid
    bounding_box_anns = 'http://www.image-net.org/downloads/bbox/bbox/' + imgnet_wnid + '.tar.gz'
    print(bounding_box_anns)

    #if we already have it, don't need to redownload
    if os.path.isfile(tar_name):
         return 1
    try:
         r = requests.get(str(bounding_box_anns))
    except: #if we can't get it, we should fail
         print("couldn't get annotations for: ", imgnet_wnid)
         quit()
         #continue
    with open(tar_name + '.gz', "wb") as code:
         code.write(r.content)

    #unzip/untar the annotations to our output directory
    subprocess.call(["/bin/gunzip", tar_name + '.gz'])
    subprocess.call(["/bin/tar", "-xvf", tar_name])
    subprocess.call(["/bin/cp", "-r", cwd + "/Annotation/" + imgnet_wnid + "/", cwd + "/" + "imgnet_annotations"])
    #cleanup annotation files
    #subprocess.call(["/bin/rm", tar_name])
    #subprocess.call(["/bin/rm", "-r", cwd + "/Annotation"])

def group_imgs_boxes(imgnet_wnid):
	#make sure we keep seeing progress
	print('group boxes->', imgnet_wnid)
	#mapping of images to bounding boxes:
	map_url = "http://www.image-net.org/api/text/imagenet.synset.geturls.getmapping?wnid=" + imgnet_wnid
	map_response = urllib.request.urlopen(map_url)
	map_data = map_response.read()
	map_text = map_data.decode('utf-8')

	grouped_dir = imgnet_grouped + '/' + imgnet_wnid
	if os.path.isdir(grouped_dir) != True:
		os.mkdir(grouped_dir)

	#get all the mappings for the wnid
	elements = map_text.split("\n")
	for i in range(0,len(elements)):
		name = elements[i]
		idx = name.find(" ")
		xml_name = name[:idx]
		idx = name.rfind("/")
		#Need to exclude the \n, otherwise we won't find the jpg image
		jpg_name = name[idx+1:-1]
		#print(xml_name, jpg_name)
		#quit()
		xml_path = imgnet_annotations + '/' + imgnet_wnid + '/' + xml_name + '.xml'
		jpg_path = imgnet_images + '/' + imgnet_wnid + '/' + jpg_name
		if os.path.isfile(xml_path) and os.path.isfile(jpg_path):
			#copy xml, jpg to grouped folder under common name
			#we will remove any unused files, so ignore them for now
			subprocess.call(["/bin/cp", xml_path, grouped_dir + '/' + xml_name + '.xml'])
			subprocess.call(["/bin/cp", jpg_path, grouped_dir + '/' + xml_name + '.jpg'])
		else:
			continue

#start of code
#for i in range(0, len(imgnet_wnid_arr)):
    #get_imgs(imgnet_wnid_arr[i])
    #get_bounding_boxes(imgnet_wnid_arr[i])
    #this function will put all jpg/xml files in one folder after matching/modifying image names
    #group_imgs_boxes(imgnet_wnid_arr[i])
    #quit()

#convert the annotations to yolo format
#manipast is manifast file, record location of image you are converting
manifast_loc = cwd + '/'
imgpath = imgnet_grouped
img_type = ".jpg"
voc = VOC(names_loc + '/imgnet.names', imgnet_classes)
yolo = YOLO(os.path.abspath(names_loc + "/dumping.names"))

for i in range(0, len(imgnet_wnid_arr)):
	grouped_dir = imgnet_grouped + '/' + imgnet_wnid_arr[i]
	if os.path.isdir(imgnet_yolo_format + '/' + imgnet_wnid_arr[i]) != True:
		os.mkdir(imgnet_yolo_format + '/' + imgnet_wnid_arr[i])
	#copy all the relevant .jpg images to the folder
	#print(grouped_dir + '/*.jpg')
	#print(imgnet_yolo_format + '/' + imgnet_wnid_arr[i])
	#quit()
	subprocess.call(["/bin/cp " + grouped_dir + '/*.jpg' + " " + imgnet_yolo_format + '/' + imgnet_wnid_arr[i]], shell=True)
        
	#Convert all the annotations at the end
	flag, data = voc.parse(imgnet_grouped + '/' + imgnet_wnid_arr[i])

	if flag == True:
		flag, data = yolo.generate(data)
		if flag == True:
			#save_path, img_path, img_type, manipast_path
			flag, data = yolo.save(data, imgnet_yolo_format + '/' + imgnet_wnid_arr[i] + '/', imgnet_images + '/' + imgnet_wnid_arr[i] + '/', img_type, manifast_loc)

		if flag == False:
			print("Saving Result : {}, msg : {}".format(flag, data))

		else:
			print("YOLO Generating Result : {}, msg : {}".format(flag, data))

	else:
		print("VOC Parsing Result : {}, msg : {}".format(flag, data))

#remove any images/txt files that have size = 0
quit()
