import OBD_IO
import obd_sensors
import time
import os
import datetime
import gpsdData
gps = gpsdData.GpsPoller()
for i in range(50):
    print ("test:   : " + str(gps.getLong()) + " - " + str(gps.getLat())+ "  - " +str(gps.getName()) )
    
    
#\\\\.\\CNCB0
obd = OBD_IO.OBDPort('/dev/pts/2', 1, 5)
def timestamp(format):
     ts = time.time()
     if format == 2:
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S:%f')[:-4]
     elif format == 1:
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H.%M')
     return st

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
