import OBD_IO
import obd_sensors

obd = OBD_IO.OBDPort("/dev/pts/2", 1, 5)

for i in range (20):
    obd.send_command("010c")
    obd.interpret_result(obd.get_result())
    rpm = obd_sensors.rpm(output)
    print(rpm)

print("Sucess!")