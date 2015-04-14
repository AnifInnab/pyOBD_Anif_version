import OBD_IO
import obd_sensors

obd = OBD_IO.OBDPort("/dev/pts/2", 1, 5)

for i in range (20):
    obd.send_command("010d")
    print(obd.get_result())
    obd.send_command("010c")
    print(obd.get_result())

print("Sucess!")