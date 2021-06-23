# -*- coding: utf-8 -*-
"""
/* ----------------------------------------------------------------------------
 *         PalmSens Method SCRIPT SDK
 * ----------------------------------------------------------------------------
 * Copyright (c) 2016-2020, PalmSens BV
 *
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * - Redistributions of source code must retain the above copyright notice,
 * this list of conditions and the disclaimer below.
 *
 * PalmSens's name may not be used to endorse or promote products derived from
 * this software without specific prior written permission.
 *
 * DISCLAIMER: THIS SOFTWARE IS PROVIDED BY PALMSENS "AS IS" AND ANY EXPRESS OR
 * IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT ARE
 * DISCLAIMED. IN NO EVENT SHALL PALMSENS BE LIABLE FOR ANY DIRECT, INDIRECT,
 * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
 * OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 * LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
 * EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 * ----------------------------------------------------------------------------
 */
"""
###############################################################################
# Description
###############################################################################
# This example showcases how to perform a simple Cyclic Voltammetry (CV) 
# measurement and output the results to the console.

###############################################################################
# Imports
###############################################################################
import requests
import json
import serial      
import os.path  
import PSEsPicoLib
import time
from datetime import datetime
import sys
#import matplotlib.plot as plt
import numpy
import array
from tkinter import *
import tkinter as tk
import tkinter.font as tkFont
import time

###############################################################################
# Configuration
###############################################################################

#Folder where scripts are stored
MSfilepath = "./MethodSCRIPT files" #Review: fixed current path for Linux  "." 
#Name of script file to run
MScriptFile = "MSExampleCV.mscr"

#COM port of the EmStat Pico
myport = "/dev/ttyUSB0"

###############################################################################
# Code
###############################################################################
i=0
mylines = []
applied_pot = []
we_current = []
record_time =[]
api_url="https://pscloudrestapi.azurewebsites.net/" # Add your api url here later on
root = None
dfont = None
frame = None
app_pot = None
we_curr = None

fullscreen = False

#combine the path and filename 
MScriptFile = os.path.join(MSfilepath, MScriptFile)

#initialization and open the port
ser = serial.Serial()   #Create an instance of the serial object

#Set printing verbosity to false
PSEsPicoLib.SetPrintVerbose(False)


# Toggle fullscreen
def toggle_fullscreen(event=None):

    global root
    global fullscreen

    # Toggle between fullscreen and windowed modes
    fullscreen = not fullscreen
    root.attributes('-fullscreen', fullscreen)
    resize()

# Return to windowed mode
def end_fullscreen(event=None):

    global root
    global fullscreen

    # Turn off fullscreen mode
    fullscreen = False
    root.attributes('-fullscreen', False)
    resize()

# Automatically resize font size based on window size
def resize(event=None):

    global dfont
    global frame

    # Resize font based on frame height (minimum size of 12)
    # Use negative number for "pixels" instead of "points"
    new_size = -max(12, int((frame.winfo_height() / 10)))
    dfont.configure(size=new_size)

#Check if port is connected to device
def init():
    if PSEsPicoLib.OpenComport(ser,myport,1):   #open myport with 1 sec timeout
      print("Succesfuly opened: " + ser.port  )
      try:
        PSEsPicoLib.Flush(ser)                       #Flush the EmstatPico parse buffer
        if PSEsPicoLib.IsConnected(ser):             #Check if EmstatPico is connected
          print("Connected!")
          #Tkinter change status to green
          print(PSEsPicoLib.GetVersion(ser))       #Print the version
          #time.sleep(2)
        else:
            #change status to red
            print("Unable to connected!")                  
      except Exception as e1:                         #catch exception 
          print("error communicating...: " + str(e1)) #print the exception
                                 #close the comport
    else:
        print("cannot open serial port ")

def poll():
    l = open("log.txt", "w")
    with open(MScriptFile) as f:             #open the script file
        content = f.readlines()             #read all the contents
        for scriptline in content:          #read the content line by line
            print(scriptline.strip(), file=l)       #print the line to send without the linefeed (stripped)
            ser.write(bytes(scriptline,  'ascii'))  #send the scriptline to the device

        #Fetch the data comming back from the device         
        while True:
            response = ser.readline()                #read until linefeed is read or timeout is expired
            res_line = response.decode("ascii")      #decode the returned bytes to an ascii string
            print("read data: " + res_line.strip(), file=l)  #print the data read without the linefeed 
            if res_line.startswith('P'):             #data point start with P
                pck = res_line[1:len(res_line)]      #ignore last and first character
                for v in pck.split(';'):             #value fields are seperated by a semicolon
                    str_vt = v[0:2]                  #get the value-type 
                    str_var = v[2:2+8]               #strip out value type, we ignore it for now
                    value = PSEsPicoLib.ParseVarString(str_var)   #Parse the value
                    var_type = PSEsPicoLib.GetVarTypeName(str_vt)   #Get the variable type  
                    var_unit = PSEsPicoLib.GetVarTypeUnit(str_vt)   #Get the unit
                    
                    currentDateTime = datetime.now()
                    record_time.append(currentDateTime.strftime("%m/%d/%Y-%H:%M:%S"))
                            
                    if var_type == "Applied potential":                                           
                        applied_pot.append(value)
                        applied_pot_unit = var_unit
                        print(value)
                        print(applied_pot, file=l)
                

                    if var_type == "WE current":                      
                        we_current.append(value)
                        we_current_unit = var_unit
                        print(value)
                        print(we_current, file=l)

                    #print(var_type + " = " +str(value) + " " + str(var_unit), file=l )
                    #i = i + 1
                    
            if (res_line == '\n'):                   #Check on termination of data from the device
                mylines = []                             # Declare an empty list named mylines.
                with open ("log.txt", 'rt') as myfile: # Open log.txt for reading text data.
                    for myline in myfile:                # For each line, stored as myline,
                        mylines.append(myline)           # add its contents to mylines.

                print(" ")
                print("*** MethodSCRIPT Parameters ***")
                print(" ")
                        
                # Mode
                pgstat_mode = mylines[3][-2]
                print('PG Stat Mode : ', pgstat_mode, file=l)

                # Bandwidth
                bw_filtered = filter(str.isdigit, mylines[4])
                bw = "".join(bw_filtered)
                bw = float(bw)
                bw_dec = mylines[4][-2]
                print('Max Bandwidth :', bw, bw_dec, 'Hz', file=l)

                # CR
                cr_filtered = filter(str.isdigit, mylines[5])
                cr = "".join(cr_filtered)
                cr = float(cr)
                cr_dec = mylines[5][-2]
                print('CR:', cr, cr_dec, file=l)

                # Autorange
                autorg = mylines[6]
                autorg = autorg.replace("set_autoranging", "")
                autorg = autorg.rstrip("\n")
                print('Autorange:', autorg, file=l)

                # E
                e_filtered = filter(str.isdigit, mylines[7])
                e = "".join(e_filtered)
                e = float(e)
                print('E:', e, 'm', file=l)   

                print(applied_pot, file=l)
                print(we_current, file=l)
                        
                print(" ")
                print("Data saved locally in log.txt")
                l.close()
                
                # saving a duplicate file as a log
                f = open(f'log-{datetime.now().strftime("%Y-%b-%d, %A %I:%M:%S")}.txt', "w")
                print(applied_pot, file=f)
                print(we_current, file=f)
                print(record_time, file=f)
                
                # now making an API request
                my_dict = {"we_current":we_current, "applied_potential":applied_pot, "measured_at":record_time}
                payload = json.dumps(my_dict)
                headers = {
                    'Content-Type': 'application/json'
                }
                try:
                    response = requests.request("POST", api_url, headers=headers, data=payload)
                    if response.status_code == 200:
                        print('Success')
                    else:
                        print("Could not complete request")
                except requests.exceptions.ConnectionError:
                    print("Could not complete request")    
                                        
                break  #exit while loop
                    
init()
poll()



