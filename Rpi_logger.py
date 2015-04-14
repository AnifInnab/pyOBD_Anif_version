import OBD_IO
import obd_sensors

obd = OBD_IO.OBDPort("/dev/pts/2", 1, 5)


obd.send_command("0100")

result = obd.get_result()
pids = obd_sensors.hex_to_bitstring(result)

print(pids)

print("Sucess!")