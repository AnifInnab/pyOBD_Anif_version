import OBD_IO

obd = OBD_IO.OBDPort("/dev/pts/2", 1, 5)

print("Sucess!")