from Tkinter import *
import tkMessageBox as messagebox
import tkFont

from test_controller import Controller

from reactor import ReactorDisplay, ValveButton

from cfg import CFG

from graph import Graph, fig

import matplotlib.animation as animation

import ttk
from ttk import *

from queue import RobotQueue

import Queue

import threading

class StackWindow:
    def __init__(self, master, idx, c, console, graph):
        self.master = master
        self.idx = idx
        self.c = c
        self.console = console
        self.graph = graph
        # master.title("Robot Control: Reactor Stack %d" % idx)
        # master.minsize(width=1600, height=800)


        self.reactors = {}




        slots = CFG['stacks']['stack %d' % idx]['slots']



        # 'Close Reactor Stack'
        self.stack_btn = ValveButton(c, self.printToConsole, CFG['stacks']['stack %d' % idx]['close reactor stack festo'],
            master, text='Close Reactor Stack %d' % idx, height=3).grid(
            row=1, column=0, sticky=N+S+E+W)

        # Reactors
        nb = ttk.Notebook(master)
        for i, e in enumerate(slots):
            # f = Frame(master)
            page = ttk.Frame(nb)
            rd = ReactorDisplay(page, int(e), c, self.printToConsole, idx, graph)
            self.reactors[int(e)] = rd
            nb.add(page, text='Reactor ' + e + '\n')
        nb.grid(row=0, column=0, columnspan=2)



        # 'Close Fitting Actuator'
        self.fitting_btn = ValveButton(c, self.printToConsole, CFG['stacks']['stack %d' % idx]['close fitting actuator festo'],
            master, text='Close Fitting Actuator').grid(
            row=1, column=1, sticky=N+S+E+W)

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
        master.minsize(width=1800, height=900)
        master.protocol("WM_DELETE_WINDOW", self.close)


        self.queue = Queue.Queue()

        # Display graph
        # self.graph = Graph(master)

        self.stacks = {}

        self.start()

        # threading.Thread(target=self.updateDisplay).start()

    def start(self):

        # Connect to controllers
        c = Controller()
        c.valve_connect()
        c.pumps_connect()
        c.ble_connect()
        self.c = c

        # tl1 = Toplevel(self.master)
        # tl1.protocol("WM_DELETE_WINDOW", self.close)

        tl1 = Frame(self.master, borderwidth=3,  relief='ridge')
        tl1.grid(row=0, column=0,sticky=N)

        tl2 = Frame(self.master, borderwidth=3,  relief='ridge')
        tl2.grid(row=0, column=1, rowspan=2, sticky=E+W+N+S)
        self.master.grid_columnconfigure(1, minsize=700)
        self.master.grid_rowconfigure(0, minsize=700)
        self.master.grid_rowconfigure(1, minsize=150)
        self.graph = Graph(tl2)

        # Make console
        self.console = Text(tl1, height=8, bg='light grey', state = DISABLED)
        self.console.grid(row=4, column=0, pady=10, sticky=E+N+S+W)
        sb = Scrollbar(tl1)
        sb.grid(row=4, column=1, sticky=N+S+W)
        sb.config(command=self.console.yview)
        self.console.config(yscrollcommand=sb.set)

        helv = tkFont.Font(family='Helvetica', size=14)
        nb = ttk.Notebook(tl1)

        # Stack Frames
        f_out = Frame(nb, borderwidth=3,  relief='ridge')
        # f_out.grid(row=0, column=0, padx=10, pady=20)
        # Label(f_out, text='STACK 1', anchor=S, font=helv).grid(row=0, column=0, columnspan=2,)
        f1 = Frame(f_out)
        s1 = StackWindow(f1, 0, c, self.console, self.graph)
        self.stacks[0] = s1
        f1.grid(row=1, column=0)
        nb.add(f_out, text='Stack 1\n')

        f_out2 = Frame(nb, borderwidth=3,  relief='ridge')
        # f_out2.grid(row=1, column=0, padx=10, pady=20)
        f2 = Frame(f_out2)
        # Label(f_out2, text='STACK 2', anchor=S, font=helv).grid(row=0, column=0)
        s2 = StackWindow(f2, 1, c, self.console, self.graph)
        self.stacks[1] = s2
        f2.grid(row=1, column=0)
        nb.add(f_out2, text='Stack 2\n')

        nb.grid(row=0, column=0)


        # Display queueing options
        tl3 = Frame(self.master)
        self.robot_queue = RobotQueue(tl3, self.print_to_console, self.stacks, self.queue)
        tl3.grid(row=1, column=0, sticky=N+E+W)


    def print_to_console(self, msg):
        self.console.config(state=NORMAL)
        self.console.insert(END, '\n' + str(msg) )
        self.console.config(state=DISABLED)
        self.console.see(END)

    count = 0
    def updateDisplay(self):
        # print 'updating'
        # self.stacks[0].reactors[0].read_id_btn.btn['text'] = str(self.count)
        self.count += 1
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)
                # self.stacks[0].reactors[0].ble_id['text'] = 'boi'
                # self.stacks[0].reactors[0].on_reactor_type_change('1ml (00795)')
                # Check contents of message and do what it says
                # As a test, we simply print it
                print 'msg' + str(msg)
                func = msg[0]
                args = msg[1:]
                func(*args)


            except Queue.Empty:
                pass

        self.master.after(100, self.updateDisplay)
        



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