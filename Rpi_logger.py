import OBD_IO
import obd_sensors
import time
import datetime
import gpsdData
#gps = gpsdData.GpsPoller()
#print ("test:   : " + gps.getLong())
obd = OBD_IO.OBDPort("/dev/pts/1", 1, 5)
inner = ""

for i in range (50):
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    seq = ('[TIME, '+ st + ']')
    inner = ""
    test = "00001010000010101000001010100000"
    '''(obd.get_sensor_valueobd_sensors.SENSORS[0])[i]''' 
    for i in range (32):
        if test[i] == '1':
            seq += "[" + obd_sensors.SENSORS[i+1].cmd + ": " + str(obd.get_sensor_value(obd_sensors.SENSORS[i+1]))  + "]"
    print(seq)
    seq = ""
print("Sucess!")