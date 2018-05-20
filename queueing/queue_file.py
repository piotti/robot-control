from Tkinter import *

from queue_api import TIMEOUT_CALLS, BLOCKING_CALLS

COLOR_EXECUTING = 'yellow'
COLOR_FINISHED = 'blue'
COLOR_ERROR = 'red'
COLOR_FILE = '#256d47'


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
        self.color_console_line(-1, COLOR_FILE)

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
        self.color_console_line(self.file_idx-1, COLOR_ERROR) 



    def mode_change(self, auto):
        if not auto and self.command in TIMEOUT_CALLS:
            self.color_console_line(self.file_idx-1, COLOR_FINISHED)

    def done_executing(self):
        if self.file_idx > 0:
            self.color_console_line(self.file_idx-1, COLOR_FINISHED)


    def seek(self, direction):
        # direction: negative for backwards, positive for forwards
        current = self.file_idx-1
        print 'current,', current

        if 0 <= current+direction < len(self.lines):
            if current >= 0:
                self.color_console_line(current, 'black')
            self.color_console_line(current + direction, 'blue')
            self.file_idx += direction
            self.console.yview('%d.0' % (self.file_idx-3))

        else:
            print 'out of range'


    def parse_line(self, idx):
        line = self.lines[idx]
        parts = line.split(',')
        step, action = parts[:2]
        arg1 = parts[2].strip() if len(parts) > 2 else ''
        arg2 = parts[3].strip() if len(parts) > 3 else ''
        arg3 = parts[4].strip() if len(parts) > 4 else ''
        step = int(step.strip())
        action = action.strip()
        arg1 = arg1.strip()

        return (step, action, arg1, arg2, arg3)



    def get_next_line(self, auto):

        while self.file_idx < len(self.lines):
            
            (step, action, arg1, arg2, arg3) = self.parse_line(self.file_idx)
            self.command = action

            # Highlight line
            if self.command in BLOCKING_CALLS:
                if self.command in TIMEOUT_CALLS and not auto:
                    self.color_console_line(self.file_idx, COLOR_FINISHED)
                else:
                    self.color_console_line(self.file_idx, COLOR_EXECUTING)
            else:
                self.color_console_line(self.file_idx, COLOR_FINISHED)

            # Unhighlight previous line
            if self.file_idx > 0:
                self.color_console_line(self.file_idx - 1, 'black')

            self.file_idx += 1

            # Scroll to line
            self.console.yview('%d.0' % (self.file_idx-3))

            return (step, action, arg1, arg2, arg3)

        return None

    def repeat_line(self, auto):
        if self.file_idx == 0:
            # nothing to be repeated (haven't started yet)
            return None
        line =  self.parse_line(self.file_idx-1)

        # Highlight line
        if self.command in BLOCKING_CALLS:
            if self.command in TIMEOUT_CALLS and not auto:
                self.color_console_line(self.file_idx-1, COLOR_FINISHED)
            else:
                self.color_console_line(self.file_idx-1, COLOR_EXECUTING)
        else:
            self.color_console_line(self.file_idx-1, COLOR_FINISHED)

        return line

    def color_console_line(self, line, color):
        self.console.tag_config('line %d' % (line+1), foreground=color)

    def print_to_console(self, msg, tag=None):
        start = self.console.index("end-1c")

        self.console.config(state=NORMAL)
        self.console.insert(END,str(msg)+'\n')
        self.console.config(state=DISABLED)

        end = self.console.index("end-2c")

        if tag is not None:
            # Add tag for later coloring
            self.console.tag_add(tag, start, end)