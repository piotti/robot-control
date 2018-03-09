from Tkinter import *
import tkMessageBox as messagebox

from ble.client import Dongle as BleDongle
from pumps.sock import PumpController 
from valves.modbus import ValveController

   
class MainWindow:

    def __init__(self, master):
        self.master = master
        master.title("Robot Control")
        master.minsize(width=1400, height=700)
        master.protocol("WM_DELETE_WINDOW", self.close)



    def close(self):
        self.master.destroy()




if __name__ == '__main__':
    root = Tk()
    my_gui = MainWindow(root)
    root.mainloop()