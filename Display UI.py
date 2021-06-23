import hashlib
import os
from datetime import datetime
from tkinter import *
import serial
import http.client as httplib
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PSEsPicoLib
matplotlib.use("TkAgg")


def read_old():
    with open('log.txt', 'r') as f:
        first_val = f.readline()[:-2]  # removing \n at the end of the line
        second_val = f.readline()[:-2]
    first_val = first_val.strip('][').split(', ')
    second_val = second_val.strip('][').split(', ')
    for i in range(0, len(first_val)):
        first_val[i] = float(first_val[i])
    for i in range(0, len(second_val)):
        second_val[i] = float(second_val[i])
    return first_val, second_val


def read_and_clean_file():
    # opening file using with() method
    # so that file get closed
    # after completing work
    fname = 'log.txt'
    N = 7
    with open(fname, 'r') as file:
        # loop to read iterate
        # last n lines and print it
        vals = []
        for line in (file.readlines()[-N:]):
            vals.append(line.rstrip())
        pg_stat_mode = vals[0]
        max_bandwidth = vals[1]
        cr = vals[2]
        autorange = vals[3]
        val_e = vals[4]
        first_val = vals[5].strip('][').split(', ')
        second_val = vals[6].strip('][').split(', ')

        for i in range(0, len(first_val)):
            first_val[i] = float(first_val[i])
        for i in range(0, len(second_val)):
            second_val[i] = float(second_val[i])
        return pg_stat_mode, max_bandwidth, cr, autorange, val_e, first_val, second_val


class Form:
    def __init__(self):
        
        #########

        # Folder where scripts are stored
        self.MSfilepath = "./MethodSCRIPT files"  # Review: fixed current path for Linux  "."
        # Name of script file to run
        self.MScriptFile = "MSExampleCV.mscr"

        # COM port of the EmStat Pico
        self.myport = "/dev/ttyUSB0"
        # combine the path and filename
        self.MScriptFile = os.path.join(self.MSfilepath, self.MScriptFile)

        # initialization and open the port
        self.ser = serial.Serial()  # Create an instance of the serial object

        # Set printing verbosity to false
        PSEsPicoLib.SetPrintVerbose(False)
        #########
        
        self.root = Tk()
        # defining size to the form
        self.root.geometry("500x500")
        self.count = 0
        self.usb_status = True
        self.wifi_status = ''
        self.hash_val = self.get_digest("log.txt")
        self.update_time = datetime.now().strftime("%H:%M:%S")

        # defining the title of form
        self.root.title('Status')
        
        self.pg_stat_mode = ""
        self.max_bandwidth = ""
        self.cr = ""
        self.autorange = ""
        self.val_e = ""
        
        self.first_val = ""
        self.second_val = ""

        self.root.attributes('-zoomed', True)

        self.figure1 = plt.Figure(figsize=(9, 10), dpi=100)
        self.ax1 = self.figure1.add_subplot(111)
        self.pg_stat_mode,self.max_bandwidth,self.cr,self.autorange,self.val_e, self.first_val, self.second_val = read_and_clean_file()
        self.canvas = FigureCanvasTkAgg(self.figure1, self.root)
        self.ax1.plot(self.first_val, self.second_val)
        self.ax1.set_title('Measurement at \n' + self.update_time)
        self.ax1.set_xlabel('Applied Potential')
        self.ax1.set_ylabel('WE Current')
        self.ax1.grid(True)
        self.canvas.get_tk_widget().pack(side=LEFT, fill=BOTH)
        self.canvas.draw_idle()

        label_0 = Label(self.root, text="Visualization", width=20, height=3, font=("bold", 25))

        # placing them in specific position
        label_0.pack()

        self.label_2 = Label(self.root, text="USB Status: " , width=30, font=("bold", 15),
                             height=5)
        self.label_2.pack()
        
        self.label_4 = Label(self.root, text="Wifi Status: ", width=30, font=("bold", 15),
                             height=5)
        self.label_4.pack()
        self.label_pg = Label(self.root, text="MethodScript Parameters:", width=30, font=("bold", 15),
                              height=1)
        self.label_pg.pack()

        self.label_pg = Label(self.root, text=str(self.pg_stat_mode), width=30, font=("bold", 15),
                              height=1)
        self.label_pg.pack()

        self.label_max_band = Label(self.root, text=str(self.max_bandwidth), width=30, font=("bold", 15),
                                    height=1)
        self.label_max_band.pack()

        self.label_cr = Label(self.root, text=str(self.cr), width=30, font=("bold", 15),
                              height=1)
        self.label_cr.pack()

        self.label_auto = Label(self.root, text=str(self.autorange), width=30, font=("bold", 15),
                                height=1)
        self.label_auto.pack()
        self.label_val = Label(self.root, text=str(self.val_e), width=30, font=("bold", 15),
                         height=1)
        self.label_val.pack()


        self.label_3 = Label(self.root, text=" ", width=50, font=("bold", 15),
                             height=2)
        self.label_3.pack()

        # this creates button for submitting the details provides by the user
        Button(self.root, text='Exit Viz', width=15, height=2, bg="black", fg='white', command=self.quit).pack()
    
        # this will run the mainloop.
        self.get_usb_status()
        self.get_wifi_status()
        self.root.after(5000, self.myloop)
        self.root.mainloop()

    def quit(self):
        # this function exits the program
        self.root.destroy()

    def update_chart(self):
        self.ax1.clear()
        self.pg_stat_mode,self.max_bandwidth,self.cr,self.autorange,self.val_e, self.first_val, self.second_val = read_and_clean_file()
        # self.canvas = FigureCanvasTkAgg(self.figure1, self.root)
        
        self.label_pg.config(text=self.pg_stat_mode)
        self.label_max_band.config(text=self.max_bandwidth)
        self.label_cr.config(text=self.cr)
        self.label_auto.config(text=self.autorange)
        self.label_val.config(text=self.val_e)
        
        self.ax1.plot(self.first_val, self.second_val)
        self.update_time = datetime.now().strftime("%H:%M:%S")
        self.ax1.set_title('Measurement at \n' + self.update_time)
        self.ax1.set_xlabel('Applied Potential')
        self.ax1.set_ylabel('WE Current')
        self.ax1.grid(True)
        self.canvas.get_tk_widget().pack(side=LEFT, fill=BOTH)
        self.canvas.draw()

    def myloop(self):
        # update USB status here...
        # for now just updating it to be off and on every 10 seconds
        self.update_chart()
        self.get_usb_status()
        self.get_wifi_status()

        new_hash = self.get_digest('log.txt')
        if new_hash != self.hash_val:
            self.label_3.config(text="Updated Log file available, please update the chart.")

        self.root.after(5000, self.myloop)

    def refresh(self):
        self.root.destroy()
        self.__init__()
        
    def get_wifi_status(self):
        url = "www.google.com"
        timeout = 3
        conn = httplib.HTTPConnection(url, timeout=timeout)
        try:
            conn.request("HEAD", "/")
            conn.close()
            self.wifi_status = 'Connected'
        except Exception as e:
            self.wifi_status = 'Disconnected'
        self.label_4.config(text="Wifi Status: " + self.wifi_status)


    def get_digest(self, file_path):
        h = hashlib.sha256()

        with open(file_path, 'rb') as file:
            while True:
                # Reading is buffered, so we can read smaller chunks.
                chunk = file.read(h.block_size)
                if not chunk:
                    break
                h.update(chunk)

        return h.hexdigest()
    
    def get_usb_status(self):
        try:
            if PSEsPicoLib.OpenComport(self.ser, self.myport, 1):  # open myport with 1 sec timeout
                print("Succesfuly opened: " + self.ser.port)
                try:
                    PSEsPicoLib.Flush(self.ser)  # Flush the EmstatPico parse buffer
                    if PSEsPicoLib.IsConnected(self.ser):  # Check if EmstatPico is connected
                        print("Connected!")
                        self.usb_status = "Connected"
                        self.label_2.config(text="USB Status: " + str(self.usb_status))
                    else:
                        # change status to red
                        print("Unable to connected!")
                        self.usb_status = "Unable to connect"
                        self.label_2.config(text="USB Status: " + str(self.usb_status))
                except Exception as e1:  # catch exception
                    print("error communicating...: " + str(e1))  # print the exception
                    self.usb_status = "Error Communicating."
                    self.label_2.config(text="USB Status: " + str(self.usb_status))
            else:
                print("cannot open serial port ")
        except:
            self.usb_status = "Unable to connect"
            self.label_2.config(text="USB Status: " + str(self.usb_status))
            



if __name__ == '__main__':
    # instantiating the form
    app = Form()

# TODO
# fix the function so that it handles the new log.txt file : DONE
# make it chart automatically updated : DONE
# make USB connected or not connected work : DONE
# maybe make it work on rasppi : DONE

