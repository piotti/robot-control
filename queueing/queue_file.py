from Tkinter import *

from queue_api import TIMEOUT_CALLS, BLOCKING_CALLS


class QueueFileManager:

    def __init__(self, console):
        self.console = console
        self.command = None


    def open_file(self, fname):
        self.fname = fname
        self.file_idx = 0
        self.lines = []
        self.command = None

        for line in open(fname, 'r').readlines()[1:]:
            line = line.strip()
            if not line:
                continue
            if line[0] == '#':
                continue
            self.lines.append(line.strip())

        # Clear console
        self.console.config(state=NORMAL)
        self.console.delete(1.0,END)
        self.console.config(state=DISABLED)

        # Delete previous tag
        for tag in self.console.tag_names():
            self.console.tag_delete(tag)


        # Display file name
        self.print_to_console(fname.split('/')[-1], tag='line 0')
        self.color_console_line(-1, 'blue')

        # Display whole file in console
        for i, l in enumerate(self.lines):
            self.print_to_console(l.strip(), tag='line %d' % (i+1))



    def reset(self):
        # Make all lines black
        for i in range(len(self.lines)):
            self.color_console_line(i, 'black')

        # Scroll to top
        self.console.see(1.0)

        # Reset pointer
        self.file_idx = 0


    def error(self):
        self.color_console_line(self.file_idx-1, 'red') 



    def mode_change(self, auto):
        if not auto and self.command in TIMEOUT_CALLS:
            self.color_console_line(self.file_idx-1, 'blue') 

        # if self.file_idx > 0 and not executing:
        #     self.color_console_line(self.file_idx-1, 'blue' if auto else 'purple') 

    def done_executing(self):
        if self.file_idx > 0:
            self.color_console_line(self.file_idx-1, 'blue') 



    def get_next_line(self, auto):

        while self.file_idx < len(self.lines):
            line = self.lines[self.file_idx]

            command = line.split(',')[1].strip()
            self.command = command

            # Highlight line
            if command in BLOCKING_CALLS:
                if command in TIMEOUT_CALLS and not auto:
                    self.color_console_line(self.file_idx, 'blue')
                else:
                    self.color_console_line(self.file_idx, 'yellow')
            else:
                self.color_console_line(self.file_idx, 'blue')

            # Unhighlight previous line
            self.color_console_line(self.file_idx - 1, 'black')

            self.file_idx += 1

            # Scroll to line
            self.console.see('%d.0' % (self.file_idx+5))

              
            return line

        return None

    def repeat_line(self, auto):
        if self.file_idx == 0:
            # nothing to be repeated (haven't started yet)
            return None
        return self.lines[self.file_idx-1]




    def color_console_line(self, line, color):
        self.console.tag_config('line %d' % (line+1), foreground=color)



    def print_to_console(self, msg, tag=None):


        start = self.console.index("end-1c")


        self.console.config(state=NORMAL)
        self.console.insert(END,str(msg)+'\n')
        self.console.config(state=DISABLED)
        # self.console.see(END)

        
        end = self.console.index("end-2c")

        if tag is not None:
            # Add tag for later coloring
            self.console.tag_add(tag, start, end)