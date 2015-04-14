import OBD_IO
import obd_sensors

obd = OBD_IO.OBDPort("/dev/pts/2", 1, 5)

for i in range (20):
    print(obd_sensors.SENSORS[I].shortname + obd.get_sensor_value(obd_sensors.SENSORS[i]) + obd_sensors.SENSORS[i].unit)

print("Sucess!")