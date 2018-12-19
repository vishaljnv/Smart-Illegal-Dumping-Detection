#Author: Siddharth Chawla
#Revision: v0.0 replaces editImage.py 
#About: Embeds exif data(GPS specifically) in images

import io 
from PIL import Image
import piexif
import read
import sys
import serial
from decimal import *
def getexifcompatibledata(inputdata):
    
    str_data = str(inputdata)
    split_input = str_data.split('.')
    deno = 10 ** len(split_input[1])
    num =  split_input[0]+ split_input[1]
    num = int(num)
    return num,deno   

def initialize_uart(dev):
    return read.init(dev)


def readgps(message):    
    if 'GNGGA' in message:
        return read.parseGGA(message)


def generate_exif_dict(gps_dict,lat_dms,long_dms):
    
    print(lat_dms['s']) 
    lat_sec_num,lat_sec_deno= getexifcompatibledata(lat_dms['s'])
    long_sec_num,long_sec_deno=getexifcompatibledata(long_dms['s']) 
    print(long_sec_num,long_sec_deno) 
    gps_ifd = {
    piexif.GPSIFD.GPSLatitudeRef:gps_dict['Lat_ref'].encode('ascii','ignore'),
    piexif.GPSIFD.GPSLatitude:((lat_dms['d'],1),(lat_dms['m'],1),(lat_sec_num,lat_sec_deno)),
    piexif.GPSIFD.GPSLongitudeRef:gps_dict['Long_ref'].encode('ascii','ignore'),
    piexif.GPSIFD.GPSLongitude:((long_dms['d'],1),(long_dms['m'],1),(long_sec_num,long_sec_deno))
    }
    exif_dict={"GPS":gps_ifd}
    return exif_dict

def degreetodms(degree):
    d=int(degree)
    m=int((degree-d)*60)
    s=float(degree-d-float(Decimal(m)/Decimal(60)))*3600
    #s=float(degree-d-float(m)/60)*3600
    return {'d':d,'m':m,'s':s}

def transform(gps_dict):
    
    gps_dict['Long'],gps_dict['Lat']= read.getlongandlat_in_degrees(gps_dict['Long'],gps_dict['Lat'])
    lat_dms=degreetodms(gps_dict['Lat'])
    long_dms=degreetodms(gps_dict['Long'])
    return lat_dms,long_dms      
