 #!/usr/bin/env python

          
      
import time
import serial
import datetime
import geocoder
from enum import Enum

GGA=[]
LOCAL_TIMEZONE = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
API_KEY= 'UwKcPqj3bzhx3USXvFRHA9GsTkO9hWWa'

class GGAEnum(Enum):
    UTCtime=1
    Lat=2
    Lat_dir=3
    Long=4
    Long_dir=5
    Fixquality=6
    numberofsatellites=7

def utctocurrent_tmzone(LOCAL_TIMEZONE):
    pass

def parselatandlong(Longitude, Long_dir, Lat, Lat_dir):
    if Lat_dir == "S":
        Lat = -1 * float(Lat) /100
    else:
        Lat=float(Lat)/100
    if Long_dir == "W":
        Long = -1 * float(Longitude) /100
    else:
        Long= float(Long)/100
    return Lat, Long

def parseGGA(inputGGA):
    GGA=inputGGA.split(",")
    if GGA[GGAEnum.Fixquality.value]==0:   
        print("Invalid Data")
    else:
        Long     = GGA[GGAEnum.Long.value]
        Long_dir = GGA[GGAEnum.Long_dir.value]
        Lat      = GGA[GGAEnum.Lat.value]
        Lat_dir  = GGA[GGAEnum.Lat_dir.value]
        Lat, Long= parselatandlong(Long, Long_dir, Lat, Lat_dir)
        print("Lat= ",Lat,"and Long= ", Long)
        print("Number of satellites", GGA[GGAEnum.numberofsatellites.value])
        #findplace(Lat, Long)
        findplace(37.331149, -121.874717) 

def findplace(Lat, Long):
    g=geocoder.mapquest([Lat,Long], method='reverse' , key= API_KEY)
    print("Place= ", g)

ser = serial.Serial(
   
    port='/dev/ttyS0',
    baudrate = 9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)


while 1:
    x=ser.readline()
    #print(x)
    x= x.decode("utf-8") 
    if 'GNGGA' in x:
        parseGGA(x)
        


