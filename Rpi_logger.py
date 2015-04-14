import OBD_IO
import obd_sensors

obd = OBD_IO.OBDPort("/dev/pts/2", 1, 5)

for i in range (20):
    obd.send_command("010c")
    result = obd.get_result()
    output = OBD_IO.interpret_result(result)
    rpm = obd_sensors.rpm(output)
    print(rpm)

print("Sucess!")