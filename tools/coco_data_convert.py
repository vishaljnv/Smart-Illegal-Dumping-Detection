#!/usr/bin/python3
#Test the COCO APIs
#Get all relevant COCO data
#Convert COCO annotations to YOLO
#Only get data with our relevant classes
import matplotlib
from pycocotools.coco import COCO
import numpy as np
import skimage.io as io
import matplotlib.pyplot as plt
import pylab
#!/usr/bin/python3
import os
import argparse
from YoloFormat import VOC, YOLO2COCO, UDACITY, KITTI, YOLO

pylab.rcParams['figure.figsize'] = (8.0, 10.0)

parser = argparse.ArgumentParser(description="Coco data conversion")
parser.add_argument('--input_loc', nargs='?', default="./",
                    help='Input location, e.g. val2014')
parser.add_argument('--data_format', nargs='?', default="2014",
                    help='Year info for formatting, e.g. 2014')
parser.add_argument('--output_loc', nargs='?', default="./",
                    help='Output location')
parser.add_argument('--names_loc', nargs='?', default="./",
                    help='names of classes file')
args = parser.parse_args()
dataType=args.input_loc
output_loc=args.output_loc
format_type = args.data_format
names_loc = args.names_loc
if format_type == "2014":
	prepend = "COCO_" + dataType + "_"
else:
	prepend = ""

show_img = 0
cwd = os.getcwd()

#Right now, we are only looking at the 2017 validation set data
dataDir='.'
#dataType='val2014'
annFile='{}/annotations/instances_{}.json'.format(dataDir,dataType)
coco=COCO(annFile)

#Get all of the imgIds for the Coco categories we are interested in
catNms=['person','backpack','bottle','chair', 'couch','dining table','tv','microwave oven','toaster']
catIds = coco.getCatIds(catNms=catNms);
imgIds_arr = []
imgIds = coco.getImgIds(catIds=catIds );
for i in range(0,len(catIds)):
	imgIds = coco.getImgIds(catIds=catIds[i])
	imgIds_arr.append(imgIds)
for i in range(0,len(imgIds_arr)):
	print(len(imgIds_arr[i]), "photos of", catNms[i])
	#print(imgIds_arr[i])
#quit()
img_id = imgIds_arr[0][0]
#img = coco.loadImgs(img_id)[0]
img = coco.loadImgs(95132)[0]
print(dir(img))
#img = coco.loadImgs(imgIds[np.random.randint(0,len(imgIds))])[0]

# load and display image
# I = io.imread('%s/images/%s/%s'%(dataDir,dataType,img['file_name']))
# use url to load image
I = io.imread(img['coco_url'])
print(img['coco_url'])
plt.axis('off')
plt.imshow(I)
if show_img == 1:
	plt.show()

# load and display instance annotations
plt.imshow(I); plt.axis('off')
annIds = coco.getAnnIds(imgIds=img['id'], catIds=catIds, iscrowd=None)
anns = coco.loadAnns(annIds)
print(anns)
coco.showAnns(anns)
if show_img == 1:
	plt.show()

#get the path for all images in this folder
print("img_id:", img_id)
img_path = '{}/{}/{}{:0>12d}.jpg'.format(os.getcwd(),dataType,prepend,img_id)
print(img_path)
J = io.imread(img_path)
plt.axis('off')
plt.imshow(J)
if show_img == 1:
	plt.show()

#manipast is manifast file, record location of image you are converting
manifast_loc = cwd + '/' + output_loc + '/'
imgpath = dataType
yolo_annotations = "yolo_annotations_coco_" + dataType
img_type = ".jpg"
#give location for this record file
#imgpath is where the jpg images are located

#Location to save annotations:
if os.path.isdir(output_loc + "/" + yolo_annotations) != True:
    os.mkdir(output_loc + "/" + yolo_annotations)

#convert the image annotations to YOLO format
#Load format converter/parser object
coco = YOLO2COCO()
#Load class names
#coco.names is a file with each desired class on a separate line
#TBD - use final .names file here?  will it create a problem?
yolo = YOLO(os.path.abspath(names_loc))

#parse coco annotation label
flag, data = coco.parse(annFile)

if flag == True:
	#if we parsed successfully, create yolo annotation data
	flag, data = yolo.generate(data)

	#If we generated yolo annotation successfully, save the data
	if flag == True:
		#save_path, img_path, img_type, manipast_path
		flag, data = yolo.save(data, cwd + "/" + output_loc + "/" + yolo_annotations + "/", "./" + imgpath + "/",
img_type, manifast_loc)

		#yolo save failed
		if flag == False:
			print("Saving Result : {}, msg : {}".format(flag, data))
	#yolo generate failed
	else:
		print("YOLO Generating Result : {}, msg : {}".format(flag, data))
#coco parse failed
else:
	print("COCO Parsing Result : {}, msg : {}".format(flag, data))
