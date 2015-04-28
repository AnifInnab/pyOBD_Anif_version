from __future__ import division
import OBD_IO
import obd_sensors
import time
import os
import datetime
import threading
#import gpsdData
    
#\\\\.\\CNCB0

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


class logger:
    def __init__(self):
        self.obd = OBD_IO.OBDPort('/dev/pts/2', 1, 5)
        self.totFuelConsumed = 0
        self.totSpeedChange = 0
        self.totVechSpeed = 0
        self.totVechRPM = 0
        self.fuelCost = 0
        self.nrOfResponses = 0.000000001
        self.timeGone = 0
        self.meters = 0
        self.nrOfStops = 0
        self.stopTrigger = 1
        self.fuelConsumed = 0
        self.carSTOP = True
        self.seq = ""
       
        self.startLogging()

    def timestamp(self, format):
         ts = time.time()
         if format == 2:
            st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S:%f')[:-4]
         elif format == 1:
            st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H.%M.%S')
         return st
    def calcEco(self):
         meanSpeed = (self.totVechSpeed/self.nrOfResponses)
         meanRPM = self.totVechRPM/self.nrOfResponses
         meanSpeedChange = self.totSpeedChange/self.nrOfResponses

         hours = (self.timeGone/3600)
         fe = (meanSpeed*100)/(0.0001 + meanRPM/100)
         se = ((75*self.nrOfStops)/(0.0001 + hours))
         te =  (meanSpeedChange*20)
         ecopoints = (fe) - se - te
         return ecopoints
    def pidsSupported(self):
        print("Retrieving supported pids...\n")
        carSens = self.obd.get_sensor_value(obd_sensors.SENSORS[0])
        print(carSens+"\n")
        for i in range (31):
            if carSens[i] == "1":
                print(obd_sensors.SENSORS[i+1].name + ":    IS SUPPORTED")
            else:
                print(obd_sensors.SENSORS[i+1].name + ":    NOT SUPPORTED")
        return carSens
    def showData(self, currentSpeed, curRPM, curMAF):
         meanSpeed = (self.totVechSpeed/self.nrOfResponses)
         meanRPM = self.totVechRPM/self.nrOfResponses
         meanSpeedChange = self.totSpeedChange/self.nrOfResponses

         print("Current speed: " + str(currentSpeed) + " km/h")
         print("Current RPM: " + str(curRPM) + " rpm")
         print("Current MAF: " + str(curMAF)+" grams/sec \n")
         print("Mean Speed: " + str(int(round(meanSpeed))) + " km/h")
         print("Mean RPM: " + str(int(round(meanRPM))) + " rpm")
         print("nrOfStops: " + str(self.nrOfStops))

         print("Mean change in speed: " + str(int(round(meanSpeedChange))) + "km/h per seconds")
    
         if(self.meters<1000):
            print("Distance traveled: " + str(round(self.meters)) + "m")
         elif(self.meters<10000):
            print("Distance traveled: " + str(round(self.meters/1000, 1)) + "km")
         else:
            print("Distance traveled: " + str(round(self.meters/10000, 2)) + " mil")
    def fuelConsumption(self, curMAF, currentSpeed):
        
         print("Fuelprice: 13kr")
         if(curMAF>0):
            mpg = (710.7 * currentSpeed) / (curMAF*100)
         else:
            mpg = 0

         if(currentSpeed>0):
            lp100km = (3600*curMAF*100)/(9069.90*currentSpeed)
         else:
             lp100km = 0
         lpm = lp100km / 100000
     
     
         print("MPG: " + str(mpg))
         print("liters per 100km: " + str(lp100km))
     
         mps = currentSpeed/3.6

         fuelConsumed = mps * lpm
         print(fuelConsumed)
         print("Fuel Consumed: " + str(fuelConsumed))
         self.totFuelConsumed += fuelConsumed
         self.fuelCost += fuelConsumed*13

         print("Fuelcost: " + str(round(self.fuelCost, 2)) + " kr")
         print("total fuelconsumption: " + str(round(self.totFuelConsumed, 2)) + " liter")
    def writePidToFile(self, command, result):
        self.seq += "[" + command + ", " + result + "]"
    def startLogging(self):
        filename = self.timestamp(1) #Get filename in timestampformat(1)
        startTime = time.time()
        #curMAF = self.obd.get_sensor_value(obd_sensors.SENSORS[16])

        ts1 = filename
        file = open(filename, "a")
        
        file.write("[UID: JHJ0ekidS93_dk3145kIssW_Kj92rIesdDj]\n")  #RASPBERRY SERIAL (UNIQE ID) CHANGE THIS LATER 

        '''####################### WRITE DTC #########################
        self.obd.send_command("0101")
        nrOfDTC = self.obd.nrOfDTC(self.obd.get_result())
        print(nrOfDTC)
        if nrOfDTC != 0:
            self.obd.send_command("03")
            dtc = self.obd.interpret_DTCresult( self.obd.get_result() )
            dtcCodes = (OBD_IO.decrypt_dtc_code(dtc, nrOfDTC))
            for i in range (int(nrOfDTC)):
                self.writePidToFile("ERROR", dtcCodes[i])
            file.write(self.seq + "\n")
        ###########################################################'''

        carSens = self.pidsSupported()  #GET SUPPORTED PIDS
        temptime = -1
        while 1:
    
            self.timeGone = int(((time.time())-startTime)) #Current time - starting time

            if self.timeGone>temptime:  #If seconds changes
                self.seq = ('[TIME, '+ self.timestamp(2) + ']' +"[GPS: " + str(gpsd.fix.longitude) + ", " + str(gpsd.fix.latitude) + "]" )
                #self.seq += ("[GPS: " + str(self.gps.getLat()) + ", " + str(self.gps.getLong()) + "]")  ## IF GPS TURNED ON
       
                ## MOST IMPORTANT PIDS (RPM, SPEED, MAF) ##
                sensorvalue = self.obd.get_sensor_value(obd_sensors.SENSORS[12])
                self.writePidToFile("010c", str(sensorvalue))
                self.totVechRPM += sensorvalue
                curRPM = sensorvalue

                sensorvalue = self.obd.get_sensor_value(obd_sensors.SENSORS[13])
                self.writePidToFile("010d", str(sensorvalue))
                curSpeed = sensorvalue
                self.totVechSpeed += sensorvalue
        
                ## MAF NOT ALL VECHICLE SUPPORT    -  GET SUPPORT FOR NON-MAF VECHICLES  -  IMAP = RPM * MAP / IAT  -  MAF = (IMAP/120)*(VE/100)*(ED)*(MM)/(R)
                sensorvalue = self.obd.get_sensor_value(obd_sensors.SENSORS[16])
                self.writePidToFile("0110", str(sensorvalue))
                curMAF = sensorvalue
                ## 
                print("________________________________________\n")
                print("time gone: " + str(self.timeGone) + "s")
                print("nrOfResponses: " + str(self.nrOfResponses))
                print("Responses per second: " + str(round(self.nrOfResponses/(self.timeGone+0.0001),2)))
        
                self.showData(curSpeed, curRPM, curMAF)
                self.fuelConsumption(curMAF, curSpeed)
                print ("Eco-points: " + str(round(self.calcEco())))
        
                self.seq += "\n"
                file.write(self.seq)
                file.flush()
                self.seq = ""

                newFileName = ts1 + " - " + self.timestamp(1)
                if(filename != newFileName):
                    file.close()
                    os.rename(filename, newFileName) 
                    file = open(newFileName, "a")
                    filename = newFileName

                self.meters += curSpeed/3.6
                self.nrOfResponses += 1
                temptime = self.timeGone
                





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
