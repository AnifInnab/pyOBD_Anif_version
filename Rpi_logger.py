import OBD_IO
import obd_sensors
import time
import datetime
obd = OBD_IO.OBDPort("/dev/pts/4", 1, 5)
inner = ""

for i in range (20):
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    seq = ('[TIME, '+ st + ']')
    inner = ""

    for i in range (32):
        if obd.PIDSSupported[i] == True:
            seq += "[" + obd_sensors.SENSORS[i].shortname + ": " + str(obd.get_sensor_value(obd_sensors.SENSORS[i])) + " " + obd_sensors.SENSORS[i].unit  + "]"
    print(seq)
    seq = ""
print("Sucess!")