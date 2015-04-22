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
nrOfResponses = 0
totVechSpeed = 0
totSpeedChange = 0
totVechRPM = 0
count = 0
currentSpeed = 0
nrOfStops = 0
trigger = 1
distance = 0
carSTOP = True
def timestamp(format):
     ts = time.time()
     if format == 2:
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S:%f')[:-4]
     elif format == 1:
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H.%M.%S')
     return st

def calcEco():
     meanSpeed = (totVechSpeed/nrOfResponses)
     meanRPM = totVechRPM/nrOfResponses
     meanSpeedChange = totSpeedChange/nrOfResponses
     hours = (timeGone/3600)
     instDistance = (currentSpeed * 0.621371192)/3600 # speed in MPH
     instFuel = 1/(1.53125 * curMAF + 0.001)
     mpg = (710.7 * currentSpeed) / (curMAF*100*1.609)
     lp100km = (3600*curMAF*100)/(9069.90*currentSpeed)
     print("Current speed: " + str(currentSpeed))
     print("MPG: " + str(mpg))
     print("liters per 100km: " + str(lp100km))
     print("Mean Speed: " + str(int(round(meanSpeed))) + "km/h")
     print("Mean RPM: " + str(int(round(meanRPM))) + "rpm")
     print("Mean change in speed: " + str(int(round(meanSpeedChange))) + "km/h per seconds")
     if(meters<1000):
        print("Distance traveled: " + str(round(meters)) + "m")
     elif(meters<10000):
        print("Distance traveled: " + str(round(meters/1000, 1)) + "km")
     else:
        print("Distance traveled: " + str(round(meters/10000, 2)) + " mil")
     fe = (meanSpeed*100)/(0.0001 + meanRPM/100)
     se = ((75*nrOfStops)/(0.0001 + hours))
     te =  (meanSpeedChange*20)
     ecopoints = (fe) - se - te
     return ecopoints




    #longitude = str(gpsd.fix.longitude)
    #latitude = str(gpsd.fix.latitude)
    #print("[GPS TEST: " + longitude + ", " + latitude + "]")
    #time.sleep(2)
filename = timestamp(1)
ts = time.time()
starttime = ts
startTime = int(datetime.datetime.fromtimestamp(ts).strftime('%S'))

ts1 = filename
file = open(filename, "a")
file.write("[UID: JHJ0ekidS93_dk3145kIssW_Kj92rIesdDj]\n")
carSens = obd.get_sensor_value(obd_sensors.SENSORS[0])
print (carSens)
meters = 0
temptimekmh = -70
temptimerpm = 0
curMAF = obd.get_sensor_value(obd_sensors.SENSORS[16]) + 1
lastSpeed = obd.get_sensor_value(obd_sensors.SENSORS[13])
while 1:
    
    ts = time.time()
    timeGone = int((ts-starttime))
    if timeGone>temptimekmh:
        
        '''+"[GPS: " + str(gpsd.fix.longitude) + ", " + str(gpsd.fix.latitude) + "]" '''
        seq = ('[TIME, '+ timestamp(2) + ']'   )
    
        for i in range (2,32):
            if carSens[i] == '1':
                seq += "[" + obd_sensors.SENSORS[i+1].cmd + ": " + str(obd.get_sensor_value(obd_sensors.SENSORS[i+1]))  + "]"
                ##ECHODRIVING CALCULATION
                if obd_sensors.SENSORS[i+1].cmd == "010D":  #speed per sec
                    currentSpeed = obd.get_sensor_value(obd_sensors.SENSORS[i+1])
                    totVechSpeed += currentSpeed
                    if currentSpeed>20:
                        carSTOP = False
                        trigger = 0
                    elif currentSpeed<5:
                        carSTOP = True
                        if trigger != 1:
                            nrOfStops += 1
                        trigger = 1
                    if count > 0:
                        if(currentSpeed>lastSpeed):
                            totSpeedChange += (currentSpeed - lastSpeed)
                            if((currentSpeed - lastSpeed)>20):
                                print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  Hard acceleration!")
                        elif(currentSpeed<lastSpeed):
                            totSpeedChange += (lastSpeed - currentSpeed)
                            if((lastSpeed-currentSpeed)>20):
                                print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx Hard Brake!")
                        elif(currentSpeed==lastSpeed):
                            totSpeedChange += 0
                        lastSpeed = currentSpeed
                        count = 0
                elif obd_sensors.SENSORS[i+1].cmd == "010C":  #rpm
                    totVechRPM += obd.get_sensor_value(obd_sensors.SENSORS[i+1])
                elif obd_sensors.SENSORS[i+1].cmd == "0110":  #MAF
                    curMAF = obd.get_sensor_value(obd_sensors.SENSORS[i+1])  
                temptimekmh = timeGone
                count += 1
                ##
        #print(seq)
        nrOfResponses += 1
        count+=1
        #print("tot vechspeed: " + str(totVechSpeed))
        #print("tot vechRPM: " + str(totVechRPM))
        #print("Tot SpeedChange: " + str(totSpeedChange))
    
        print("-----------------------------------")
        if(timeGone<300):
            print("time gone: " + str(timeGone) + "s")
        else:
            print("time gone: " + str(round(timeGone/60 , 1)) + " min")
        print("nrOfResponses: " + str(nrOfResponses))
        print("Responses per second: " + str(round(nrOfResponses/(timeGone+0.0001),2)))
        
        print("nrOfStops: " + str(nrOfStops))
        meters += currentSpeed/3.6

        ecopoints = calcEco()
        print ("Eco-points: " + str(int(ecopoints)))
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
    
print ("\nKilling Thread...")
gpsp.running = False
gpsp.join() # wait for the thread to finish what it's doing
print ("Done.\nExiting.")