from Tkinter import *
import Queue
import os

class ThreadSafeConsole(Text):
    def __init__(self, master, **options):
        Text.__init__(self, master, **options)
        self.insert_queue = Queue.Queue()
        self.update_me()
        self.idx = 0
    def write(self, line, color=None):
        self.insert_queue.put((line, color))
    def clear(self):
        self.insert_queue.put((None, None))

    def update_me(self):
        try:
            while 1:
                line, color = self.insert_queue.get_nowait()
                self.config(state=NORMAL)
                start = self.index("end-1c")
                if line is None:
                    self.delete(1.0, END)
                else:
                    self.insert(END, str(line))
                self.config(state=DISABLED)
                self.see(END)
                end = self.index("end-2c")

                if color is not None:
                    self.tag_add(str(self.idx), start, end)
                    self.tag_config(str(self.idx), foreground=color)
                    self.idx += 1

                self.update_idletasks()
        except Queue.Empty:
            pass
        self.after(100, self.update_me)