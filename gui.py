from Tkinter import *
import tkMessageBox as messagebox
import tkFont

from test_controller import Controller

from reactor import ReactorDisplay, ValveButton

from cfg import CFG

from graph import Graph, fig

import matplotlib.animation as animation

import ttk

class StackWindow2:
    def __init__(self, master, idx, c, console):
        self.master = master
        self.idx = idx
        self.c = c
        self.console = console
        # master.title("Robot Control: Reactor Stack %d" % idx)
        # master.minsize(width=1600, height=800)


        slots = CFG['stacks']['stack %d' % idx]['slots']



        # 'Close Reactor Stack'
        ValveButton(c, self.printToConsole, CFG['stacks']['stack %d' % idx]['close reactor stack festo'],
            master, text='Close Reactor Stack %d' % idx).grid(
            row=0, column=0, sticky=N+S)

        # Reactors
        nb = ttk.Notebook(master)
        for i, e in enumerate(slots):
            # f = Frame(master)
            page = ttk.Frame(nb)
            rd = ReactorDisplay(page, int(e), c, self.printToConsole)
            nb.add(page, text='Reactor ' + e)
        nb.grid(row=0, column=1)



        # 'Close Fitting Actuator'
        ValveButton(c, self.printToConsole, CFG['stacks']['stack %d' % idx]['close fitting actuator festo'],
            master, text='Close Fitting Actuator').grid(
            row=0, column=2, sticky=N+S)

        # Add pumps callback to print to console
        self.c.add_pump_callback(lambda msg: self.printToConsole('Pump message received: %s' % msg))

       

    def printToConsole(self, msg):
        self.console.config(state=NORMAL)
        self.console.insert(END, '\n' + str(msg) )
        self.console.config(state=DISABLED)
        self.console.see(END)


class StackWindow:
    def __init__(self, master, idx, c):
        self.master = master
        self.idx = idx
        self.c = c
        master.title("Robot Control: Reactor Stack %d" % idx)
        master.minsize(width=1600, height=800)


        slots = CFG['stacks']['stack %d' % idx]['slots']

        # Make console
        self.console = Text(master, height=6, bg='light grey', state = DISABLED)
        self.console.grid(row=6, column=0, columnspan=3, pady=10, sticky=E)
        sb = Scrollbar(self.master)
        sb.grid(row=6, column=3, sticky=N+S+W)
        sb.config(command=self.console.yview)
        self.console.config(yscrollcommand=sb.set)

        # 'Close Reactor Stack'
        ValveButton(c, self.printToConsole, CFG['stacks']['stack %d' % idx]['close reactor stack festo'], master, text='Close Reactor Stack %d' % idx, height=len(slots)*10).grid(row=0, rowspan=len(slots), column=0)

        # Reactors
        for i, e in enumerate(slots):
            f = Frame(master)
            f.grid(row=i, column=1, sticky=N)
            rd = ReactorDisplay(f, int(e), c, self.printToConsole)


        # 'Close Fitting Actuator'
        ValveButton(c, self.printToConsole, CFG['stacks']['stack %d' % idx]['close fitting actuator festo'], master, text='Close Fitting Actuator', height=len(slots)*10).grid(row=0, rowspan=len(slots), column=2)

        # Add pumps callback to print to console
        self.c.add_pump_callback(lambda msg: self.printToConsole('Pump message received: %s' % msg))

       

    def printToConsole(self, msg):
        self.console.config(state=NORMAL)
        self.console.insert(END, '\n' + str(msg) )
        self.console.config(state=DISABLED)
        self.console.see(END)


   
class MainWindow:

    def __init__(self, master):
        self.master = master
        master.title("Robot Control")
        master.minsize(width=1000, height=800)
        master.protocol("WM_DELETE_WINDOW", self.close)

        # Display graph
        self.graph = Graph(master)

        
        self.start()       

    def start(self):

        # Connect to controllers
        c = Controller()
        c.valve_connect()
        c.pumps_connect()
        c.ble_connect()
        self.c = c

        tl1 = Toplevel(self.master)
        tl1.protocol("WM_DELETE_WINDOW", self.close)

        # Make console
        self.console = Text(tl1, height=6, bg='light grey', state = DISABLED)
        self.console.grid(row=4, column=0, pady=10, sticky=E)
        sb = Scrollbar(tl1)
        sb.grid(row=4, column=1, sticky=N+S+W)
        sb.config(command=self.console.yview)
        self.console.config(yscrollcommand=sb.set)

        # Stack Frames
        Label(tl1, text='STACK 1', anchor=S).grid(row=0, column=0, columnspan=2, pady=10)
        f1 = Frame(tl1)
        s1 = StackWindow2(f1, 1, c, self.console)
        f1.grid(row=1, column=0)
        f2 = Frame(tl1)
        # tl2 = Toplevel(self.master)
        # tl2.protocol("WM_DELETE_WINDOW", self.close)
        Label(tl1, text='STACK 2', anchor=S).grid(row=2, column=0, columnspan=2, pady=20)
        s2 = StackWindow2(f2, 2, c, self.console)
        f2.grid(row=3, column=0)

        



    def close(self):
        print 'closing...'
        self.c.valve_disconnect()
        self.c.pumps_disconnect()
        self.master.destroy()
        exit()




if __name__ == '__main__':
    # Create GUI
    root = Tk()
    my_gui = MainWindow(root)

    # Start graph animation
    ani = animation.FuncAnimation(fig, my_gui.graph.animate, interval=1000)

    # Run program loop
    root.mainloop()