from Tkinter import *
import tkMessageBox as messagebox

# from ble.client import Dongle as BleDongle
# from pumps.sock import PumpController 
# from valves.modbus import ValveController

from reactor import ReactorDisplay, ValveButton

from cfg import CFG

class StackWindow:
    def __init__(self, master, idx):
        self.master = master
        self.idx = idx
        master.title("Robot Control: Reactor Stack %d" % idx)
        master.minsize(width=1600, height=1200)
        master.protocol("WM_DELETE_WINDOW", self.close)


        slots = CFG['stacks']['stack %d' % idx]['slots']

        # 'Close Reactor Stack'
        ValveButton(master, text='Close Reactor Stack %d' % idx, height=len(slots)*8).grid(row=0, rowspan=len(slots), column=0)

        # Reactors
        for i, e in enumerate(slots):
            f = Frame(master)
            f.grid(row=i, column=1, sticky=N)
            rd = ReactorDisplay(f, int(e))
        Label(master, height=8, width=12).grid(row=5, column=1, stick=W)


        # 'Close Fitting Actuator'
        ValveButton(master, text='Close Fitting Actuator', height=len(slots)*8).grid(row=0, rowspan=len(slots), column=2)


    def close(self):
        self.master.destroy()
        exit()

   
class MainWindow:

    def __init__(self, master):
        self.master = master
        master.title("Robot Control")
        master.minsize(width=100, height=100)
        master.protocol("WM_DELETE_WINDOW", self.close)

        # Stack Windows
        s1 = StackWindow(Toplevel(self.master), 1)
        s2 = StackWindow(Toplevel(self.master), 2)



    def close(self):
        self.master.destroy()
        exit()




if __name__ == '__main__':
    root = Tk()
    my_gui = MainWindow(root)
    root.mainloop()