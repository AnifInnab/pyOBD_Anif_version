import OBD_IO
import obd_sensors

obd = OBD_IO.OBDPort("/dev/pts/2", 1, 5)

for i in range (20):
    print(obd.get_sensor_value("010c"))

print("Sucess!")