import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style

import Tkinter as tk

import time

import os

from cfg import CFG


LARGE_FONT= ("Verdana", 12)
style.use("ggplot")

fig = Figure(figsize=(5,5), dpi=100)
a = fig.add_subplot(211)
b = fig.add_subplot(212)


START_TIME = None


import random
def addNewPoint():
    global count
    TEMP_SETS[0].add(random.randint(0, 3000) )
    PRESSURE_SETS[0].add(random.randint(0, 30))



class FileWriter:
    def __init__(self):
        self.started = False

        self.data_queue = []


    def start(self):
        if self.started:
            return
        self.started = True

        # Check if folder data folder exists
        date = time.strftime('%m-%d-%y')
        if not os.path.isdir('logs/'+date):
            # Create date folder
            os.mkdir('logs/'+date)
        # create file name
        self.fpath = 'logs/' + date + '/' + time.strftime('%m-%d-%y %H %M')
        # Check if file exists
        if os.path.isfile(self.fpath+'.txt'):
            # Start iterating through all files with this timestamp
            count = 1
            while os.path.isfile('%s (%d).txt' % (self.fpath, count)):
                count += 1
            self.fpath = '%s (%d)' % (self.fpath, count)
        # Create and open new file
        # file = open(self.fpath+'.csv', 'w')
        # print 'created file %s' % self.fpath+'.csv'
        # # Create CVS header
        # reactors = []
        # for stack in CFG['stacks']:
        #     for slot in CFG['stacks'][stack]['slots']:
        #         reactors.append(slot)
        # header = 'Time,','.join('P%s,T%s' % (r, r) for r in reactors)
        # header = 'Time,' + header
        # file.write(header + '\n')
        # file.close()

        # # get indicies of each reactor
        # self.r_inds = {e:reactors.index(e) for e in reactors}



    def queue(self, typ, name, y, t):
        self.data_queue.append( (typ, name.replace(' ', '_'), y, t) )

    def write(self): 
        if not self.started:
            self.start()   
        # Write queued data to file
        if self.data_queue:
            # open file
            file = open(self.fpath+'.txt', 'w')
            for line in self.data_queue:
                file.write('%s %s %.3f %.2f\n' % line)
            file.close()


fw = FileWriter()




class DataSet:

    def __init__(self, typ, name):
        self.typ = typ
        self.name = name
        # self.num = name[8:]
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

        # Write to file
        fw.queue(self.typ, self.name, y, t-START_TIME)

        # If dataset more than 1000 points long, delete off end
        if len(self.ts) > 1000:
            self.ts.pop(0)
            self.ys.pop(0)

    def __repr__(self):
        return str((self.ts, self.ys))

TEMP_SETS = []
PRESSURE_SETS = []

def add_temp_set(*args, **kwargs):
    ds = DataSet('T', *args, **kwargs)
    TEMP_SETS.append(ds)
    return ds
def add_pressure_set(*args, **kwargs):
    ds = DataSet('P', *args, **kwargs)
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

        self.a_xlim = (0,120)
        self.a_ylim = (0,300)
        self.b_xlim = (0,120)
        self.b_ylim = (0,200)





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
        # addNewPoint()

        print 'datasets', TEMP_SETS

        ### Configure Temp Subplot ###
        series = []
        tMax = 0
        yMax = 0
        yMin = 0
        for ds in TEMP_SETS:
            if not ds.ts:
                continue
            series.append(ds.ts + [time.time()-START_TIME])
            series.append(ds.ys + [ds.ys[-1]])
            tMax = max(ds.ts[-1], tMax)
            yMax = max(yMax, ds.ymax)
            yMin = min(yMin, ds.ymin)
            # Add placeholder data point at end to make line go all the way to current time


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
                self.a_ylim = (0,300)#(min(yMin, self.a_ylim[0]), max(yMax, self.a_ylim[1]))
            a.set_ylim(self.a_ylim)
        else:
            lim = a.get_ylim()
            self.a_ylim = lim[0], lim[1]
        a.callbacks.connect('xlim_changed', self.on_a_xlims_change)
        a.callbacks.connect('ylim_changed', self.on_a_ylims_change)

        # Write to file
        fw.write()


        ### Configure Pressure Subplot ###
        series = []
        tMax = 0
        yMax = 0
        yMin = 0
        for ds in PRESSURE_SETS:
            if not ds.ts:
                continue
            series.append(ds.ts + [time.time()-START_TIME])
            series.append(ds.ys + [ds.ys[-1]])
            tMax = max(ds.ts[-1], tMax) if ds.ts else 0
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
                self.b_ylim = (0,200)#(min(yMin, self.b_ylim[0]), max(yMax, self.b_ylim[1]))
            b.set_ylim(self.b_ylim)
        else:
            lim = b.get_ylim()
            self.b_ylim = lim[0], lim[1]
        # b.callbacks.connect('xlim_changed', self.on_b_xlims_change)
        b.callbacks.connect('ylim_changed', self.on_b_ylims_change)



if __name__=='__main__':
    root = tk.Tk()
    app = Graph(root)

    add_temp_set('One')
    add_pressure_set('Two')
    

    ani = animation.FuncAnimation(fig, app.animate, interval=1000)
    root.mainloop()