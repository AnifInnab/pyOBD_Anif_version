import module1
import os
from gps import *
from time import *
import time
import threading
 
gpsd = None #seting the global variable

os.system('clear') #clear the terminal (optional)
 
class GpsPoller(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    global gpsd #bring it in scope
    gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
    self.current_value = None
    self.running = True #setting the thread running to true
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
    
if __name__ == '__main__':
  gpsp = GpsPoller() # create the thread
  try:
    gpsp.start() # start it up
    while True:
      #It may take a second or two to get good data
      print ("sho: "+ gpsd.fix.latitude +  ", " + gpsd.fix.longitude  +  ", " + Time + ",gpsd.utc ")
  

      gpsd.fix.latitude
      gpsd.fix.longitude

 
  
  except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    print ("\nKilling GPS Thread...")
    gpsp.running = False
    gpsp.join() # wait for the thread to finish what it's doing
  print ("Done.\nExiting.")



logger = module1.logger()