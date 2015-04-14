import serial
import string
import time
from math import ceil
from datetime import datetime

import obd_sensors
from obd_sensors import hex_to_int

GET_DTC_COMMAND   = "03"
CLEAR_DTC_COMMAND = "04"
GET_FREEZE_DTC_COMMAND = "07"

class OBDPort:
     """ OBDPort abstracts all communication with OBD-II device."""
     def __init__(self,portnum,SERTIMEOUT,RECONNATTEMPTS):
         """Initializes port by resetting device and gettings supported PIDs. """
         # These should really be set by the user.
         baud     = 38400
         databits = 8
         par      = serial.PARITY_NONE  # parity
         sb       = 1                   # stop bits
         to       = SERTIMEOUT
         self.ELMver = "Unknown"
         self.State = 1 #state SERIAL is 1 connected, 0 disconnected (connection failed)
         self.port = None
         
         print("Opening interface (serial port)")

         try:
             self.port = serial.Serial(portnum,baud, \
             parity = par, stopbits = sb, bytesize = databits,timeout = to)
             
         except serial.SerialException as e:
             print (e)
             self.State = 0
             return None
             
         print("Interface successfully " + self.port.portstr + " opened")
         print("Connecting to ECU...")
         
         try:
            self.send_command("atz")   # initialize
            time.sleep(1)
         except serial.SerialException:
            self.State = 0
            return None
            
         self.ELMver = self.get_result()
         if(self.ELMver is None):
            self.State = 0
            return None
         
         print("atz response:" + self.ELMver)
         self.send_command("ate0")  # echo off
         print("ate0 response:" + self.get_result())
         self.send_command("0100")
         ready = self.get_result()
         test = '10101011101001010101010100101010'
         self.PIDSSupported = False*32
         for i in range (32):
             #str(obd.get_sensor_value(obd_sensors.SENSORS[0]))[i]
            if test[i] == '1':
                PIDSSupported[i] = True

         if(ready is None):
            self.State = 0
            return None
            
         print("0100 response:" + ready)
         return None
              
     def close(self):
         """ Resets device and closes all associated filehandles"""
         
         if (self.port!= None) and self.State==1:
            self.send_command("atz")
            self.port.close()
         
         self.port = None
         self.ELMver = "Unknown"

     def send_command(self, cmd):
         """Internal use only: not a public interface"""
         if self.port:
             self.port.flushOutput()
             self.port.flushInput()
             for c in cmd:
                 self.port.write(c)
             self.port.write("\r\n")
             #debug_display(self._notify_window, 3, "Send command:" + cmd)

     def interpret_result(self,code):
         """Internal use only: not a public interface"""
         # Code will be the string returned from the device.
         # It should look something like this:
         # '41 11 0 0\r\r'
         
         # 9 seems to be the length of the shortest valid response
         if len(code) < 7:
             #raise Exception("BogusCode")
             print ("boguscode?")+code
         
         # get the first thing returned, echo should be off
         code = string.split(code, "\r")
         code = code[0]
         
         #remove whitespace
         code = string.split(code)
         code = string.join(code, "")
         
         #cables can behave differently 
         if code[:6] == "NODATA": # there is no such sensor
             return "NODATA"
             
         # first 4 characters are code from ELM
         code = code[4:]
         return code
    
     def get_result(self):
         """Internal use only: not a public interface"""
         #time.sleep(0.01)
         repeat_count = 0
         if self.port is not None:
             buffer = ""
             while 1:
                 c = self.port.read(1)
                 if len(c) == 0:
                    if(repeat_count == 5):
                        break
                    print ("Got nothing\n")
                    repeat_count = repeat_count + 1
                    continue
                    
                 if c == '\r':
                    continue
                    
                 if c == ">":
                    break;
                     
                 if buffer != "" or c != ">": #if something is in buffer, add everything
                    buffer = buffer + c
                    
             #debug_display(self._notify_window, 3, "Get result:" + buffer)
             if(buffer == ""):
                return None
             return buffer
         else:
            print("NO self.port!")
         return None

     # get sensor value from command
     def get_sensor_value(self,sensor):
         """Internal use only: not a public interface"""
         cmd = sensor.cmd
         self.send_command(cmd)
         data = self.get_result()
         
         if data:
             data = self.interpret_result(data)
             if data != "NODATA":
                 data = sensor.value(data)
         else:
             return "NORESPONSE"
             
         return data

     # return string of sensor name and value from sensor index
     def sensor(self , sensor_index):
         """Returns 3-tuple of given sensors. 3-tuple consists of
         (Sensor Name (string), Sensor Value (string), Sensor Unit (string) ) """
         sensor = obd_sensors.SENSORS[sensor_index]
         r = self.get_sensor_value(sensor)
         return (sensor.name,r, sensor.unit)

     def sensor_names(self):
         """Internal use only: not a public interface"""
         names = []
         for s in obd_sensors.SENSORS:
             names.append(s.name)
         return names
                 

     def log(self, sensor_index, filename): 
          file = open(filename, "w")
          start_time = time.time() 
          if file:
               data = self.sensor(sensor_index)
               file.write("%s     \t%s(%s)\n" % \
                         ("Time", string.strip(data[0]), data[2])) 
               while 1:
                    now = time.time()
                    data = self.sensor(sensor_index)
                    line = "%.6f,\t%s\n" % (now - start_time, data[1])
                    file.write(line)
                    file.flush()