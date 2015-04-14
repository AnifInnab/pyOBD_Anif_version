import OBD_IO

obd = OBD_IO.OBDPort("/dev/ttyUSB0", 1, 5)

print("Sucess!")