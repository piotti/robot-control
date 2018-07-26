from Tkinter import *
import Queue
import os

class ThreadSafeLabel(Label):
    def __init__(self, master, **options):
        Label.__init__(self, master, **options)
        self.insert_queue = Queue.Queue()
        self.update_me()

    def set_text(self, txt):
        self.insert_queue.put(txt)

    def update_me(self):
        try:
            while 1:
                txt = self.insert_queue.get_nowait()
                self.config(text=txt)
                self.update_idletasks()
        except Queue.Empty:
            pass
        self.after(100, self.update_me)