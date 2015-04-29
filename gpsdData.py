import os
from gps import *
from time import *
import time

 
gpsd = None #seting the global variable

os.system('clear') #clear the terminal (optional)
 
class GpsPoller():
  def __init__(self):
    global gpsd #bring it in scope
    gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
    self.current_value = None
    for i in range(30):
        print(str(gpsd.fix.longitude) + " - ")
  def run(self):
    global gpsd
    while gpsp.running:
      gpsd.next() #this will continue to loop and grab EACH set of gpsd info to clear the buffer
  def getLong(self):
    return gpsd.fix.longitude
  def getLat(self):
    return gpsd.fix.latitude
    