from __future__ import division
import OBD_IO
import obd_sensors
import time
import os
import datetime
import threading
#import gps
#import gpsdData
#\\\\.\\CNCB0

    

class logger:
    def __init__(self):
        self.obd = OBD_IO.OBDPort('\\\\.\\CNCB0', 1, 5)
        # Listen on port 2947 (gpsd) of localhost
        #self.session = gps.gps("localhost", "2947")
        #self.session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
        self.totFuelConsumed = 0
        self.totSpeedChange = 0
        self.totVechSpeed = 0
        self.totVechRPM = 0
        self.fuelCost = 0
        self.nrOfResponses = 0.000000001
        self.timeGone = 0
        self.meters = 0
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
         if(self.timeGone <1):
            meanSpeed = self.obd.get_sensor_value(obd_sensors.SENSORS[13])
            meanRPM = self.obd.get_sensor_value(obd_sensors.SENSORS[12])
            meanSpeedChange = self.totSpeedChange/self.nrOfResponses
         else:
             meanSpeed = (self.totVechSpeed/self.nrOfResponses)
             meanRPM = self.totVechRPM/self.nrOfResponses
             meanSpeedChange = self.totSpeedChange/self.nrOfResponses

         hours = (self.timeGone/3600)
         fe = (meanSpeed*100)/(0.0001 + meanRPM/100)
         se = ((75*1)/(0.0001 + hours))
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
         if(self.timeGone <2):
            meanSpeed = self.obd.get_sensor_value(obd_sensors.SENSORS[13])
            meanRPM = self.obd.get_sensor_value(obd_sensors.SENSORS[12])
            meanSpeedChange = self.totSpeedChange/self.nrOfResponses
         else:
             meanSpeed = (self.totVechSpeed/self.nrOfResponses)
             meanRPM = self.totVechRPM/self.nrOfResponses
             meanSpeedChange = self.totSpeedChange/self.nrOfResponses
         print("Current speed: " + str(currentSpeed) + " km/h")
         print("Current RPM: " + str(curRPM) + " rpm")
         print("Current MAF: " + str(curMAF)+" grams/sec \n")
         print("Mean Speed: " + str(int(round(meanSpeed))) + " km/h")
         print("Mean RPM: " + str(int(round(meanRPM))) + " rpm\n")

         print("Mean change in speed: " + str(int(round(meanSpeedChange))) + "km/h per seconds")
    
         if(self.meters<1000):
            print("Distance traveled: " + str(round(self.meters)) + "m")
         elif(self.meters<10000):
            print("Distance traveled: " + str(round(self.meters/1000, 2)) + "km")
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
     
     
         print("MPG: " + str(round(mpg, 2)))
         print("liters per 100km: " + str(round(lp100km, 2)))
     
         mps = currentSpeed/3.6

         fuelConsumed = mps * lpm
         #print(fuelConsumed)
         #print("Fuel Consumed: " + str(fuelConsumed))
         self.totFuelConsumed += fuelConsumed
         self.fuelCost += fuelConsumed*13

         print("Fuelcost: " + str(round(self.fuelCost, 2)) + " kr")
         print("total fuelconsumption: " + str(round(self.totFuelConsumed, 2)) + " liter")
    def writePidToFile(self, command, result):
        self.seq += "[" + command + "," + result + "]"
    def getDTC(self):
        self.obd.send_command("0101")
        nrOfDTC = self.obd.nrOfDTC(self.obd.get_result())
        print(nrOfDTC)
        if nrOfDTC != "NODATA":
            self.obd.send_command("03")
            dtc = self.obd.interpret_DTCresult( self.obd.get_result() )
            dtcCodes = (OBD_IO.decrypt_dtc_code(dtc, nrOfDTC))
            for i in range (int(nrOfDTC)):
                print("Engine DTC errorcode: " + dtcCodes[i] )
                self.writePidToFile("ERROR", dtcCodes[i])
            file.write(self.seq + "-\n")
            time.sleep(5)
    def loadGPSFIX(self):
        for i in range (5):
            report = self.session.next()
            print (report)
            if report['class'] == 'TPV':
                if hasattr(report, 'time'):
                    lon = ("longitude: " + str(report.lon))
            self.session.fix.longitude
            print("Setting up GPS...")
            print("LOADING GPS... " + str(i*20) + "%")
            os.system("clear")
    def startLogging(self):
        filename = self.timestamp(1) #Get filename in timestampformat(1)

        ts1 = filename
        file = open(filename, "a")
        
        file.write("[UID, JHJ0ekidS93_dk3145kIssW_Kj92rIesdDj]-\n")  #RASPBERRY SERIAL (UNIQE ID) CHANGE THIS LATER 

        self.obd.send_command("0101")
        nrOfDTC = self.obd.nrOfDTC(self.obd.get_result())
        print(nrOfDTC)
        if nrOfDTC != "NODATA":
            self.obd.send_command("03")
            dtc = self.obd.interpret_DTCresult( self.obd.get_result() )
            dtcCodes = (OBD_IO.decrypt_dtc_code(dtc, nrOfDTC))
            for i in range (int(nrOfDTC)):
                print("Engine DTC errorcode: " + dtcCodes[i] )
                self.writePidToFile("ERROR", dtcCodes[i])
            file.write(self.seq + "-\n")
            time.sleep(5)

        carSens = self.pidsSupported()  #GET SUPPORTED PIDS
        temptime = -1
        '''
        #self.loadGPSFIX(self)
        for i in range (5):
            report = self.session.next()
            print (report)
            if report['class'] == 'TPV':
                if hasattr(report, 'time'):
                    lon = ("longitude: " + str(report.lon))
            self.session.fix.longitude
            print("Setting up GPS...")
            print("LOADING GPS... " + i*20 + "%")
            os.system("clear")
         '''
        
        startTime = time.time()
        while 1:
    
            self.timeGone = int(((time.time())-startTime)) #Current time - starting time
            if self.timeGone>temptime:  #If seconds changes

                self.writePidToFile("TIME", self.timestamp(2))
                #self.writePidToFile("GPS", (str(self.session.fix.longitude) + "-" + str(self.session.fix.latitude)))

                ## MOST IMPORTANT PIDS (RPM, SPEED, MAF) ##
                sensorvalue = self.obd.get_sensor_value(obd_sensors.SENSORS[12]) #rpm
                self.writePidToFile("010c", str(sensorvalue))
                self.totVechRPM += sensorvalue
                curRPM = sensorvalue

                sensorvalue = self.obd.get_sensor_value(obd_sensors.SENSORS[13]) #speed
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
        
                self.showData(curSpeed, curRPM, curMAF) 
                print("-   -   -   -   -   -   -   -   -   -   -\n               FUEL CONSUMPTION\n-   -   -   -   -   -   -   -   -   -   -")
                self.fuelConsumption(curMAF, curSpeed)
                #print ("Eco-points: " + str(round(self.calcEco())))
        
                self.seq += "-\n"
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
                




