import OBD_IO
import obd_sensors
import time
import os
import datetime
import threading
from gps import *




class GpsPoller(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    global gpsd #bring it in scope
    gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info

    self.current_value = None
    self.running = True #setting the thread running to true
 
  def run(self):
    global gpsd
    while gpsp.running:
      gpsd.next() #this will continue to loop and grab EACH set of gpsd info to clear the buffer
 
if __name__ == '__main__':
  gpsp = GpsPoller() # create the thread
  gpsp.start() # start it up

    
#\\\\.\\CNCB0
obd = OBD_IO.OBDPort('/dev/pts/3', 1, 5)
def timestamp(format):
     ts = time.time()
     if format == 2:
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S:%f')[:-4]
     elif format == 1:
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H.%M')
     return st



for i in range (50):
    longitude = str(gpsd.fix.longitude)
    latitude = str(gpsd.fix.latitude)
    print(longitude + ", " + latitude)
filename = timestamp(1)
ts1 = filename
file = open(filename, "a")
file.write("[UID: JHJ0ekidS93_dk3145kIssW_Kj92rIesdDj]\n")
carSens = obd.get_sensor_value(obd_sensors.SENSORS[0])
print (carSens)
while 1:
        
    seq = ('[TIME, '+ timestamp(2) + ']')
    for i in range (2,32):
        if carSens[i] == '1':
            seq += "[" + obd_sensors.SENSORS[i+1].shortname + ": " + str(obd.get_sensor_value(obd_sensors.SENSORS[i+1]))  + "]"
    print(seq)
    seq += "\n"
    file.write(seq)
    file.flush()
    seq = ""
    newFileName = ts1 + " - " + timestamp(1)
    if(filename != newFileName):
        file.close()
        os.rename(filename, newFileName) 
        file = open(newFileName, "a")
        filename = newFileName
print ("\nKilling Thread...")
gpsp.running = False
gpsp.join() # wait for the thread to finish what it's doing
print ("Done.\nExiting.")