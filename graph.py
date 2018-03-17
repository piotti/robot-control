import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style

import Tkinter as tk

import time


LARGE_FONT= ("Verdana", 12)
style.use("ggplot")

fig = Figure(figsize=(5,5), dpi=100)
a = fig.add_subplot(211)
b = fig.add_subplot(212)


START_TIME = None


import random
def addNewPoint():
    global count
    TEMP_SETS[0].add(random.randint(0, 30) )
    PRESSURE_SETS[0].add(random.randint(0, 30))



class DataSet:

    def __init__(self, name):
        self.name = name
        self.ts = []
        self.ys = []

        self.ymax = 0
        self.ymin = 0

    def add(self, y, t=None):
        if t is None:
            t = time.time()
        global START_TIME
        if START_TIME is None:
            START_TIME = t
            print 'setting start'
        print time.time()-START_TIME
        self.ts.append(t-START_TIME)
        self.ys.append(y)
        self.ymax = max(y, self.ymax)
        self.ymin = min(y, self.ymin)

TEMP_SETS = []
PRESSURE_SETS = []

def add_temp_set(*args, **kwargs):
    ds = DataSet(*args, **kwargs)
    TEMP_SETS.append(ds)
    return ds
def add_pressure_set(*args, **kwargs):
    ds = DataSet(*args, **kwargs)
    PRESSURE_SETS.append(ds)
    return ds

        

class Graph():

    def __init__(self, master):
        # label = tk.Label(master, text="Graph Page!", font=LARGE_FONT)
        # label.pack(pady=10,padx=10)
        
        canvas = FigureCanvasTkAgg(fig, master)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2TkAgg(canvas, master)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)


        self.live_scroll = tk.IntVar()
        self.live_scroll.set(1)
        tk.Checkbutton(master, text='Live Scroll', variable=self.live_scroll).pack()

        self.a_xlim = (0,60)
        self.a_ylim = (0,50)
        self.b_xlim = (0,60)
        self.b_ylim = (0,50)



    # Declare and register callbacks
    def on_a_xlims_change(self, axes):
        lim = a.get_xlim()
        # print "updated xlims: ", lim
        self.a_xlim = lim[0], lim[1]

        # Stop scrolling
        # self.live_scroll.set(0)

    def on_a_ylims_change(self, axes):
        lim =  a.get_ylim()
        # print "updated ylims: ", lim
        self.a_ylim = lim[0], lim[1]

        # Stop scrolling
        # self.live_scroll.set(0)

            # Declare and register callbacks
    def on_b_xlims_change(self, axes):
        lim = b.get_xlim()
        # print "updated xlims: ", lim
        self.b_xlim = lim[0], lim[1]

        # Stop scrolling
        # self.live_scroll.set(0)

    def on_b_ylims_change(self, axes):
        lim =  b.get_ylim()
        # print "updated ylims: ", lim
        self.b_ylim = lim[0], lim[1]

        # Stop scrolling
        # self.live_scroll.set(0)


    def animate(self, i):
        addNewPoint()

        ### Configure Temp Subplot ###
        series = []
        tMax = 0
        yMax = 0
        yMin = 0
        for ds in TEMP_SETS:
            series.append(ds.ts)
            series.append(ds.ys)
            tMax = max(ds.ts[-1], tMax)
            yMax = max(yMax, ds.ymax)
            yMin = min(yMin, ds.ymin)

        a.clear()
        a.plot(*series)
        a.legend([ds.name for ds in TEMP_SETS])
        a.set_xlabel('Time (s)')
        a.set_ylabel('Temp (C)')
        # Set limits as they were before
        if self.a_xlim is not None:
            # print 'settig xlim to ', self.xlim
            # Scroll to the right
            if tMax > self.a_xlim[1] and self.live_scroll.get():
                delta = tMax - self.a_xlim[1]
                self.a_xlim = (self.a_xlim[0]+delta, tMax)
            a.set_xlim(self.a_xlim)
        else:
            lim = a.get_xlim()
            self.a_xlim = lim[0], lim[1]
        if self.a_ylim is not None:
            # print 'setting ylim to ', ylim
            # Set vertical scaling
            if self.live_scroll.get():
                self.a_ylim = (yMin, yMax)
            a.set_ylim(self.a_ylim)
        else:
            lim = a.get_ylim()
            self.a_ylim = lim[0], lim[1]
        a.callbacks.connect('xlim_changed', self.on_a_xlims_change)
        a.callbacks.connect('ylim_changed', self.on_a_ylims_change)


        ### Configure Pressure Subplot ###
        series = []
        tMax = 0
        yMax = 0
        yMin = 0
        for ds in PRESSURE_SETS:
            series.append(ds.ts)
            series.append(ds.ys)
            tMax = max(ds.ts[-1], tMax)
            yMax = max(yMax, ds.ymax)
            yMin = min(yMin, ds.ymin)
        b.clear()
        b.plot(*series)
        b.legend([ds.name for ds in PRESSURE_SETS])
        b.set_xlabel('Time (s)')
        b.set_ylabel('Pressure (psi)')
        # Set limits as they were before
        if self.b_xlim is not None:
            # print 'settig xlim to ', self.xlim
            # Scroll to the right
            if tMax > self.b_xlim[1] and self.live_scroll.get():
                delta = tMax - self.b_xlim[1]
                # print 'settig xlim to ', self.xlim
                self.b_xlim = (self.b_xlim[0]+delta, tMax)
            b.set_xlim(self.b_xlim)
        else:
            lim = b.get_xlim()
            self.b_xlim = lim[0], lim[1]
        if self.b_ylim is not None:
            # print 'setting ylim to ', ylim
             # Set vertical scaling
            if self.live_scroll.get():
                self.b_ylim = (yMin, yMax)
            b.set_ylim(self.b_ylim)
        else:
            lim = b.get_ylim()
            self.b_ylim = lim[0], lim[1]
        b.callbacks.connect('xlim_changed', self.on_b_xlims_change)
        b.callbacks.connect('ylim_changed', self.on_b_ylims_change)



if __name__=='__main__':
    root = tk.Tk()
    app = Graph(root)

    add_temp_set('One')
    add_pressure_set('Two')
    

    ani = animation.FuncAnimation(fig, app.animate, interval=1000)
    root.mainloop()