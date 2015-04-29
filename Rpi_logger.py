from __future__ import division
import OBD_IO
import obd_sensors
import time
import os
import datetime
import threading

'''
from gps import *




class GpsPoller(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    global gpsd #bring it in scope
    gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info

    self.current_value = None
    self.running = True #setting the thread running to true
 
  def run(self):
    global gpsd
    while gpsp.running:
      gpsd.next() #this will continue to loop and grab EACH set of gpsd info to clear the buffer
 
if __name__ == '__main__':
  gpsp = GpsPoller() # create the thread
  gpsp.start() # start it up
'''
    
#\\\\.\\CNCB0
obd = OBD_IO.OBDPort('\\\\.\\CNCB0', 1, 5)
nrOfResponses = 0.000000000001
totVechSpeed = 0
totSpeedChange = 0
totVechRPM = 0
count = 0
meters = 0
temptime = -1
currentSpeed = 0
nrOfStops = 0
stopTrigger = 1
distance = 0
fuelConsumed = 0
fuelCost = 0
carSTOP = True
def timestamp(format):
     ts = time.time()
     if format == 2:
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S:%f')[:-4]
     elif format == 1:
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H.%M.%S')
     return st
def calcEco(timeGone, totVechSpeed, nrOfResponses, totVechRPM, totSpeedChange):
     meanSpeed = (totVechSpeed/nrOfResponses)
     meanRPM = totVechRPM/nrOfResponses
     meanSpeedChange = totSpeedChange/nrOfResponses

     hours = (timeGone/3600)
     fe = (meanSpeed*100)/(0.0001 + meanRPM/100)
     se = ((75*nrOfStops)/(0.0001 + hours))
     te =  (meanSpeedChange*20)
     ecopoints = (fe) - se - te
     return ecopoints
def pidsSupported():
    print("Retrieving supported pids...\n")
    carSens = obd.get_sensor_value(obd_sensors.SENSORS[0])
    print(carSens+"\n")
    for i in range (31):
        if carSens[i] == "1":
            print(obd_sensors.SENSORS[i+1].name + ":    IS SUPPORTED")
        else:
            print(obd_sensors.SENSORS[i+1].name + ":    NOT SUPPORTED")
    return carSens
def showData(totVechSpeed, nrOfResponses, totVechRPM, totSpeedChange):
     meanSpeed = (totVechSpeed/nrOfResponses)
     meanRPM = totVechRPM/nrOfResponses
     meanSpeedChange = totSpeedChange/nrOfResponses

     print("Current speed: " + str(currentSpeed) + " km/h")
     print("Current RPM: " + str(curRPM) + " rpm")
     print("Current MAF: " + str(curMAF)+" grams/sec \n")
     print("Mean Speed: " + str(int(round(meanSpeed))) + " km/h")
     print("Mean RPM: " + str(int(round(meanRPM))) + " rpm")
     print("nrOfStops: " + str(nrOfStops))

     print("Mean change in speed: " + str(int(round(meanSpeedChange))) + "km/h per seconds")
    
     if(meters<1000):
        print("Distance traveled: " + str(round(meters)) + "m")
     elif(meters<10000):
        print("Distance traveled: " + str(round(meters/1000, 1)) + "km")
     else:
        print("Distance traveled: " + str(round(meters/10000, 2)) + " mil")
def fuelConsumption(fuelConsumed, fuelCost):
     print("Fuelprice: 13kr")

     mpg = (710.7 * currentSpeed) / (curMAF*100+0.00000000000001)
     lp100km = (3600*curMAF*100)/(9069.90*currentSpeed+0.0000000001)
     lpm = 0.00001 * lp100km
     print(lpm)
     print("MPG: " + str(mpg))
     print("liters per 100km: " + str(lp100km))
     instMeter = currentSpeed/3.6
     fuelCost += fuelConsumed*13
     print("Fuelcost: " + str(fuelCost))
     return round(instMeter*lpm, 2)

#longitude = str(gpsd.fix.longitude)
#latitude = str(gpsd.fix.latitude)
#print("[GPS TEST: " + longitude + ", " + latitude + "]")
#time.sleep(2)
    

filename = timestamp(1) #Get filename in timestampformat(1)

startTime = time.time()

ts1 = filename
file = open(filename, "a")
file.write("[UID: JHJ0ekidS93_dk3145kIssW_Kj92rIesdDj]\n")  #RASPBERRY SERIAL (UNIQE ID) CHANGE THIS LATER 

carSens = pidsSupported()  #GET SUPPORTED PIDS

curMAF = obd.get_sensor_value(obd_sensors.SENSORS[16])
lastSpeed = obd.get_sensor_value(obd_sensors.SENSORS[13])
while 1:
    
    currentTime = time.time()
    timeGone = int((currentTime-startTime))

    if timeGone>temptime:  #If seconds changes
        
        '''+"[GPS: " + str(gpsd.fix.longitude) + ", " + str(gpsd.fix.latitude) + "]" '''
        seq = ('[TIME, '+ timestamp(2) + ']'   )
    
        for i in range (1,32):
            if carSens[i] == '1':
                seq += "[" + obd_sensors.SENSORS[i+1].cmd + ": " + str(obd.get_sensor_value(obd_sensors.SENSORS[i+1]))  + "]"

                if obd_sensors.SENSORS[i+1].cmd == "010D":  #speed per sec
                    currentSpeed = obd.get_sensor_value(obd_sensors.SENSORS[i+1])
                    totVechSpeed += currentSpeed
                    if currentSpeed>20:
                        carSTOP = False
                        stopTrigger = 0
                    elif currentSpeed<5:
                        carSTOP = True
                        if stopTrigger != 1:
                            nrOfStops += 1
                        stopTrigger = 1
                    if count > 0:
                        if(currentSpeed>lastSpeed):
                            totSpeedChange += (currentSpeed - lastSpeed)
                            if((currentSpeed - lastSpeed)>20):
                                print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx Hard acceleration! xxxxxxxxxxxxxxxxxxxxxx")
                        elif(currentSpeed<lastSpeed):
                            totSpeedChange += (lastSpeed - currentSpeed)
                            if((lastSpeed-currentSpeed)>20):
                                print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx Hard Brake! xxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
                        elif(currentSpeed==lastSpeed):
                            totSpeedChange += 0
                        lastSpeed = currentSpeed
                        count = 0
                elif obd_sensors.SENSORS[i+1].cmd == "010C":  #rpm
                    totVechRPM += obd.get_sensor_value(obd_sensors.SENSORS[i+1])
                    curRPM = obd.get_sensor_value(obd_sensors.SENSORS[i+1])
                elif obd_sensors.SENSORS[i+1].cmd == "0110":  #MAF
                    curMAF = obd.get_sensor_value(obd_sensors.SENSORS[i+1])  
                temptime = timeGone
                count += 1
        #print(seq)
        print("________________________________________\n")
        print("time gone: " + str(timeGone) + "s")
        print("nrOfResponses: " + str(nrOfResponses))
        print("Responses per second: " + str(round(nrOfResponses/(timeGone+0.0001),2)))
        
        showData(totVechSpeed, nrOfResponses, totVechRPM, totSpeedChange)
        fuelConsumed += fuelConsumption(fuelConsumed, fuelCost)
        print("FUEL CONSUMED: " + str(fuelConsumed) + "liter")
       
        print ("Eco-points: " + str(round(calcEco(timeGone, totVechSpeed, nrOfResponses, totVechRPM, totSpeedChange))))
        
        seq += "\n"
        file.write(seq)
        file.flush()
        seq = ""

        newFileName = ts1 + " - " + timestamp(1)
        if(filename != newFileName):
            file.close()
            os.rename(filename, newFileName) 
            file = open(newFileName, "a")
            filename = newFileName

        meters += currentSpeed/3.6
        count  += 1
        nrOfResponses += 1

    
print ("\nKilling Thread...")
gpsp.running = False
gpsp.join() # wait for the thread to finish what it's doing
print ("Done.\nExiting.")