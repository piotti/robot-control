from Tkinter import *
from ttk import *
import tkFileDialog


class RobotQueue:

    def __init__(self, master):
        self.master = master
        self.file_chosen = False

        # Make Display

        Button(master, text="Open Queue File", command=self.on_open_queue).pack()



    def on_open_queue(self):
        self.fname = tkFileDialog.askopenfilename(initialdir = "queues/",title = "Select Queue",filetypes = (("CSV files","*.csv"),("all files","*.*")))
        if not self.file_chosen:
            self.queue_label = Label(self.master, text=self.fname.split('/')[-1])
            self.queue_label.pack()
            Button(self.master, text='Start Process', command=self.on_process_start).pack()
            self.file_chosen = True
        else:
            self.queue_label['text'] = self.fname.split('/')[-1]

    def on_process_start(self):
        print 'starting process...'
