from Tkinter import *
from ttk import *
import tkFileDialog
import tkSimpleDialog

from queue_api import QueueParseException, QueueApi, BLOCKING_CALLS, TIMEOUT_CALLS
from queue_file import QueueFileManager
from settings import QueueSettings

import time

import traceback

SYMBOLS = {
    'play': u'\u2941',
    'pause': u'\u270b',
    'step': u'\u23E9',#u'\u23ED',
    'redo': u'\u21BA',
    'stop': u'\u25A0',
    'clock': u'\u23F0',#u'\u23f2',
    'arrowleft': u'\u00AB',
    'arrowright': u'\u00BB',

}

class RobotQueue:

    def __init__(self, master, cnsl_print, stacks, rheodyne_valves):
        self.master = master
        self.file_chosen = False
        self.cnsl_print = cnsl_print
        self.stacks = stacks
        self.rheodyne_valves = rheodyne_valves # CC

        # Make Display
        Label(master, text="Queuing Control", anchor=CENTER, font=("TkDefaultFont", 12)).grid(row=0, column=0, columnspan=2, sticky=E+W)
         # Make console
        self.console = Text(master, height=8, width=60, bg='light grey', state = DISABLED, font=("Consolas", 9))
        self.console.grid(row=1, column=1, sticky=E+N+S+W)
        # master.grid_columnconfigure(0, maxsize=200)
        sb = Scrollbar(master)
        sb.grid(row=1, column=2, sticky=N+S+W)
        sb.config(command=self.console.yview)
        self.console.config(yscrollcommand=sb.set)

        self.qfm = QueueFileManager(self.console)

        # Create console control buttons
        cnsl_btn_frame = Frame(master)
        cnsl_btn_frame.grid(row=1, column=0, rowspan=3, columnspan=1, sticky=N+W+S)
        s = Style()
        s.configure('basic.TButton', font=("Consolas", 14))
        s.configure('selected.TButton', font=("Consolas", 14), background='green')
        s.configure('unselected.TButton', font=("Consolas", 14), foreground='gray')
        self.manual_btn = Button(cnsl_btn_frame, text=SYMBOLS['pause'], width=3, style='unselected.TButton',command=self.on_manual)
        self.manual_btn.grid(row=0, column=0, sticky=N+W)
        self.auto_btn = Button(cnsl_btn_frame, text=SYMBOLS['play'], width=3, style='selected.TButton',command=self.on_auto)
        self.auto_btn.grid(row=0, column=1, sticky=N+W)
        Button(cnsl_btn_frame, text=SYMBOLS['stop'], width=3, style='basic.TButton', command=self.on_stop).grid(row=1, column=0, sticky=N+W+S)
        Button(cnsl_btn_frame, text=SYMBOLS['step'], width=3, style='basic.TButton', command=self.on_step).grid(row=2, column=1, sticky=N+W+S)
        Button(cnsl_btn_frame, text=SYMBOLS['redo'], width=3, style='basic.TButton', command=self.on_redo).grid(row=2, column=0, sticky=N+W+S)
        Button(cnsl_btn_frame, text=SYMBOLS['clock'], width=3, style='basic.TButton', command=self.on_timer).grid(row=1, column=1, sticky=N+W+S)
        Button(cnsl_btn_frame, text=SYMBOLS['arrowleft'], width=3, style='basic.TButton', command=self.on_arrow_left).grid(row=3, column=0, sticky=N+W+S)
        Button(cnsl_btn_frame, text=SYMBOLS['arrowright'], width=3, style='basic.TButton', command=self.on_arrow_right).grid(row=3, column=1, sticky=N+W+S)

        button_frame = Frame(master)
        button_frame.grid(row=1, column=3, rowspan=1, sticky=N)
        Button(button_frame, text="Open Queue File", width=20, command=self.on_open_queue).grid(row=0, column=0, sticky=E+W+N)
        self.queue_label = Label(button_frame, text='', font=("Consolas", 9))
        self.queue_label.grid(row=2, column=0, columnspan=3, sticky=E+W)
        self.start_btn = Button(button_frame, text='Start Process', command=self.on_process_start, state=DISABLED)
        self.start_btn.grid(row=1, column=0, sticky=E+W)

        # Spacer at bottom
        # Label(master).grid(row=3, column=0)

        # Add timer
        self.timer_label = Label(self.master, text='', foreground='blue',  font=("TkDefaultFont", 12))
        self.timer_label.grid(row=1, column=4, sticky=N, padx=10)

        # Variables to keep track of state
        self.paused = False
        self.stopped = True
        self.executing = False
        self.actions = []

        self.counter = Counter(self.master, self.timer_label)

        self.settings = QueueSettings()

        self.api = QueueApi(self.stacks, self.rheodyne_valves, self.show_info, self.counter, self.resume, self.set_control, self.settings)




    def on_auto(self):
        if not self.paused:
            return
        # play
        self.paused = False
        self.auto_btn.configure(style='selected.TButton')
        self.manual_btn.configure(style='unselected.TButton')
        self.qfm.mode_change(True)

        if not self.executing and not self.stopped:
            print 'resuming'
            self.process()

    def on_manual(self):
        if self.paused:
            return

        # pause
        self.auto_btn.configure(style='unselected.TButton')
        self.manual_btn.configure(style='selected.TButton')

        self.paused = True
        self.qfm.mode_change(False)

        # if last call was a timeout, get rid of it
        if self.actions and not self.stopped:
            if self.actions[-1] in TIMEOUT_CALLS:
                self.counter.stop()
                self.executing = False
            

    def on_stop(self):
        if self.stopped:
            return
        self.stopped = True
        self.cnsl_print('Stopping queuing process')
        self.counter.stop()
        self.qfm.reset()        

    def on_step(self):
        if not self.paused:
            self.show_info('Can\'t step while in automatic mode.')
            return
        if self.executing:
            self.show_info('Must wait for process to finish before stepping to next instruction.')
            return
        if self.stopped:
            self.init_process()

        # we're paused and want to move onto next instruction
        self.process()

    def on_redo(self):
        if self.stopped:
            return
        if not self.paused:
            self.show_info('Can\'t repeat instruction while in automatic mode.')
            return
        if self.executing:
            self.show_info('Must wait for process to finish before repeating instruction.')
            return

        # redo
        self.process(redo=True)

    def on_timer(self):
        if self.stopped:
            return
        if not self.paused:
            self.show_info('Must be in manual mode to use manual timeouts.')
            return
        if self.executing:
            self.show_info('Must wait for current process to finish.')

        timeout = tkSimpleDialog.askstring('Timeout', 'Enter timeout in seconds')
        if timeout is None:
            return

        # Create custom timeout process
        try:
            t = int(float(timeout) * 1000)
        except ValueError:
            self.show_err('Error: Couldn\'t parse input as number' % timeout)
            return

        self.actions.append('TIMEOUT')
        self.executing = True
        self.counter.start(t, self.resume)

        # put back in auto mode
        self.on_auto()

    def on_arrow_left(self):
        if self.stopped:
            return
        if not self.paused:
            self.show_info('Must be in manual mode to seek.')
            return
        if self.executing:
            self.show_info('Must wait for current process to finish.')

        # Step backwards without executing
        self.qfm.seek(-1)

    def on_arrow_right(self):
        if not self.paused:
            self.show_info('Must be in manual mode to seek.')
            return
        if self.executing:
            self.show_info('Must wait for current process to finish.')
        if self.stopped:
            self.init_process()

        # Step backwards without executing
        self.qfm.seek(1)

    def set_control(self, control):
        if control == 'manual':
            self.on_manual()
        elif control == 'auto':
            self.on_auto()

    def show_err(self, msg):
        self.cnsl_print(msg, color='red')

    def show_info(self, msg):
        self.cnsl_print(msg, color='blue')


    def on_open_queue(self):
        self.fname = tkFileDialog.askopenfilename(initialdir = "queues/",title = "Select Queue",filetypes = (("CSV files","*.csv"),("all files","*.*")))
        display_name = self.fname.split('/')[-1]
        if len(display_name) > 20:
            display_name=display_name[:17] + '...'
        if self.fname:
            self.start_btn['state'] = NORMAL
            self.queue_label['text'] = display_name

            self.qfm.open_file(self.fname)

    def init_process(self):
        # Variables stored for queueing system
        self.step = 0
        self.actions = []
        self.stopped = False
        self.retries = 0

        self.api.reset()

    def on_process_start(self):
        if not self.stopped:
            self.on_stop()
        self.init_process()
        self.process()


    def process_queue_error(self):

        # Highlight error in console 
        self.qfm.error()

        # Stop executing
        self.executing = False

        if self.paused:
            return

        command = self.actions[-1]
        handling = self.settings.get_command_error_handling(command)
        if handling['retry'] > self.retries:
            # Try again
            self.show_info('Attempting Retry %d out of %d retr%s...' % (self.retries+1, handling['retry'], 'y' if  handling['retry'] == 1 else 'ies'))
            self.retries += 1
            self.on_manual()
            self.on_arrow_left()
            self.on_auto()
            return

        else:
            # Reset retry counter
            self.retries = 0

            if handling['continue']:
                # Just keep going
                self.show_info('Execution failed but continuing anyway (overrriden in queue file)')
                self.process()
            else:
                # Go into manual mode
                self.show_info('Switching to manual mode.')
                self.on_manual()



    def handle_api_call(self, func, *args, **kwargs):
        try:
            return func(*args, **kwargs)

        except QueueParseException as e:
            if e.message is not None:
                self.show_err(e.message)
            self.process_queue_error()
            raise HandledProcessException
        except ValueError:
            self.show_err('Error - step %d: Couldn\'t parse value.' % self.step)
            self.process_queue_error()
            raise HandledProcessException
        except Exception:
            self.show_err('Error - step %d: An unknown API error occured.' % self.step)
            traceback.print_exc()
            self.process_queue_error()
            raise HandledProcessException

    def handle_parsing_call(self, func, *args, **kwargs):
        try:
            return func(*args, **kwargs)

        except ValueError:
            self.show_err('Error - step %d: Couldn\'t parse line.' % self.step)
            self.process_queue_error()
            raise HandledProcessException
        except Exception:
            self.show_err('Error - step %d: An unknown error occured when trying to parse line.' % self.step)
            traceback.print_exc()
            self.process_queue_error()
            raise HandledProcessException

    def process(self, redo=False):
        try:
            # Make sure queueing isn't stopped or paused
            if self.stopped:
                return
            
            if not redo:
                line = self.handle_parsing_call(self.qfm.get_next_line, not self.paused)
            else:
                line = self.handle_parsing_call(self.qfm.repeat_line, not self.paused)

            if line is None:
                return

            (step, action, arg1, arg2, arg3) = line
            self.cnsl_print('Step %d: %s %s %s %s' % line)

            self.executing = True        

            self.step = step
            self.actions.append(action)
            
            # parse action
            status = self.handle_api_call(self.api.parse_action, not self.paused, step, action, arg1, arg2, arg3)

            if status == 1:
                # A blocking call was made, exit and wait for callback to resume
                return

            if not self.paused:
                # process the next line
                self.process()
            else:
                # we're done executing until switched to auto or command is stepped or repeated
                self.executing = False

        except HandledProcessException:
            print 'exception handled'
            pass


    # Callback used for operations that the program must wait for to finish.
    def resume(self, msg=None):
        try:

            if self.stopped:
                return

            # Finish the last task
            action = self.actions[-1]
            self.handle_api_call(self.api.resume, action, msg, self.step)

            self.executing = False
            self.qfm.done_executing()

            if not self.paused:
                # Continue queueing where we left off
                self.process()

        except HandledProcessException:
            print 'handled exception in resume'
            pass


class Counter:
    def __init__(self, master, timer_label):
        self.master = master
        self.timer_label = timer_label

        self.stopped = True
        self.paused = False

    def start(self, time_ms, cb):
        self.stopped = False
        self.hrs = False
        self.mins = False
        self.paused = False
        self.prev_elapsed_time = 0
        self.cb = cb
        # Register callback
        self.cb_after_id = self.master.after(time_ms, self.cb)

        self.timeout = time_ms/1000.
        if self.timeout >= 60:
            self.mins = True
        if self.timeout >= 3600:
            self.hrs = True
        if self.timeout < 1:
            # No point counting
            return

        self.start_time = time.time()
        self.update()


    def pause(self):
        if self.stopped or self.paused:
            return
        self.paused = True
        # Cancel after call of callback
        self.master.after_cancel(self.cb_after_id)
        self.master.after_cancel(self.update_after_id)

        # Note how much time the timer has since last pause
        self.prev_elapsed_time += time.time() - self.start_time

    def resume(self):
        if self.stopped or not self.paused:
            return
        self.paused = False
        self.start_time = time.time()
        # Respost after call for callback
        time_left_ms = int((self.timeout - self.prev_elapsed_time)*1000)
        self.cb_after_id = self.master.after(time_left_ms, self.cb)
        self.update()

    def stop(self):
        if self.stopped:
            return
        self.stopped = True
        self.timer_label['text'] = ''
        self.master.after_cancel(self.update_after_id)



    def update(self):
        if self.paused or self.stopped:
            return

        # Time elapsed is time since last resume plus elapsed time before resume
        time_elapsed = time.time() - self.start_time + self.prev_elapsed_time


        if time_elapsed >= self.timeout:
            # Done
            self.timer_label['text'] = ''
            return

        time_left = round(self.timeout - time_elapsed)

        # Update display
        hours = int(time_left / 3600)
        minutes = int(time_left / 60) % 60
        seconds = int(time_left) % 60
        if self.hrs:
            self.timer_label['text'] = '%d:%02d:%02d' % (hours, minutes, seconds)
        elif self.mins:
            self.timer_label['text'] = '%02d:%02d' % (minutes, seconds)
        else:
            self.timer_label['text'] = '%d second%s' % (seconds, '' if seconds == 1 else 's')



        self.update_after_id = self.master.after(1000, self.update)



class HandledProcessException(Exception):
    pass






