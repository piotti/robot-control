from Tkinter import *
from ttk import *
import tkFileDialog

from cfg import CFG

import threading

class RobotQueue:

    def __init__(self, master, cnsl_print, stacks, queue):
        self.master = master
        self.file_chosen = False
        self.cnsl_print = cnsl_print
        self.stacks = stacks
        self.queue = queue

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
        # Variables stored for queueing system
        self.step = 0
        self.actions = []
        self.reactors = {}
        self.read_idx = 0

        # Open file
        self.file = open(self.fname, 'r')

        # Read Header
        self.file.readline()

        # t = threading.Thread(target=self.start_process)
        # t.start()
        try:
            self.process()
        except QueueParseException:
            self.cnsl_print('Exiting Queue Mode')
        except ValueError:
            self.cnsl_print('Error - step %d: Couldn\'t parse value.' % self.step)

    def process(self):

        while True:
            line = self.file.readline()
            self.read_idx += 1
            if line == '':
                # Whole file has been read
                break
            if line[0] == '#':
                # Its a comment, ignore
                continue
            if not line.strip():
                # Empty line
                continue
            

            parts = line.split(',')
            step, action, arg1 = parts[:3]
            arg2 = parts[3].strip() if len(parts) > 3 else ''
            arg3 = parts[4].strip() if len(parts) > 4 else ''
            step = int(step.strip())
            action = action.strip()
            arg1 = arg1.strip()
            self.step = step
            self.actions.append(action)
            self.cnsl_print('Step %d: %s %s %s %s' % (step, action, arg1, arg2, arg3))

            # parse action
            status = self.parse_action(action, arg1, arg2, arg3)
            if status == 1:
                # A blocking call was made, exit and wait for callback to resume
                return



    def parse_action(self, action, arg1, arg2, arg3):
        if action == 'REACTORSETUP':
            '''
            * Links the specified reactor to the specified reactor bay. This must be done before any
            BLE communication, or before moving a reactor to/from the bay
            * Arguments
                1. Reactor ID (Set in config file)
                2. Reactor bay, in format `x y`
            '''
            rID = int(arg1)
            x, y = arg2.split(' ')
            x = int(x)
            y = int(y)
            rtype = self.get_reactor_type_from_id(rID)
            self.get_reactor_display(x, y).on_reactor_type_change(rtype)

            # Store reactor ID for later reference
            self.reactors[rID] = (x, y)

        elif action == 'PUMPSETUP':
            '''
            * Links a pump to the specified port on the specified reactor. Must call `REACTORSETUP` first. To have the robot move the tube,
            call `PUMPCONNECT` or `PUMPDISCONNECT` after calling `PUMPSETUP`.
            * Arguments
                1. Reactor ID
                2. Port number (1, 2, 3, or 4)
                3. Tube number, correlating to a pump (see config file)
            '''
            rID = int(arg1)
            pnum = int(arg2)
            if pnum not in (1,2,3,4):
                self.cnsl_print('Error - step %d: Port number must be integer between 1 and 4.' % self.step)
                raise QueueParseException
            tnum = arg3
            if tnum not in CFG['tubes']:
                self.cnsl_print('Error - step %d: Tube "%s" not found.' % (self.step, tnum))
                raise QueueParseException    
            self.get_reactor_display(ID=rID).make_tube_number_change_callback(pnum)(tnum)

        elif action == 'REACTORMOVE':
            '''
            * Moves a reactor with the specified ID from storage to the reactor stack and vise-versa. Must call `REACTORSETUP` first to link
            reactor to reactor bay.
            * Arguments
                1. Reactor ID
                2. Direction, one of the following:
                    * `TOBAY` - move from storage to stack
                    * `TOSTORAGE` - move from stack to storage               
            '''
            rID = int(arg1)
            if arg2 == 'TOBAY':
                self.get_reactor_display(ID=rID).on_move_to_stack(callback=self.resume)
                return 1
            elif arg2 == 'TOSTORAGE':
                self.get_reactor_display(ID=rID).on_move_to_storage(callback=self.resume)
                return 1
            else:
                # Parse error
                self.cnsl_print('Error - step %d: Direction "%s" unkown. Must be "TOSTORAGE" or "TOBAY".' % (self.step, arg2))
                raise QueueParseException

        elif action == 'PUMPCONNECT':
            '''
            * Connects the pump tube. Must have previously initialized pump with `PUMPSETUP`.
            * Arguments
                1. Reactor ID
                2. Port number (1, 2, 3, or 4)
            '''
            rID = int(arg1)
            pnum = int(arg2)
            if pnum not in (1,2,3,4):
                self.cnsl_print('Error - step %d: Port number must be integer between 1 and 4.' % self.step)
                raise QueueParseException
            self.get_reactor_display(ID=rID).make_port_connect_callback(pnum)(callback=self.resume)
            return 1

        elif action == 'PUMPDISCONNECT':
            '''
            * Disconnects the pump tube. Must have previously initialized pump with `PUMPSETUP`.
            * Arguments
                1. Reactor ID
                2. Port number (1, 2, 3, or 4)
            '''
            rID = int(arg1)
            pnum = int(arg2)
            if pnum not in (1,2,3,4):
                self.cnsl_print('Error - step %d: Port number must be integer between 1 and 4.' % self.step)
                raise QueueParseException
            self.get_reactor_display(ID=rID).make_port_disconnect_callback(pnum)(callback=self.resume)
            return
        
        elif action == 'PUMPFLOWSET':
            '''
            * Sets the flow of the pump. Must have previously initialized pump with `PUMPSETUP`.
            * Arguments
                1. Reactor ID
                2. Port number (1, 2, 3, or 4)
                3. Flow value
            '''
            rID = int(arg1)
            pnum = int(arg2)
            # Make sure pump has been setup
            if self.get_reactor_display(ID=rID).tube_numbers[pnum].get() not in CFG['tubes']:
                # Error
                self.cnsl_print('Error - step %d: Port %d not configured. Make sure to call PUMPSETUP first.' % (self.step, pnum))
                raise QueueParseException

            fv = arg3
            self.get_reactor_display(ID=rID).flow_rates[pnum].delete(0, END)
            self.get_reactor_display(ID=rID).flow_rates[pnum].insert(0, fv)
            err = self.get_reactor_display(ID=rID).make_start_pump_callback(pnum)()
            if err == 1:
                # Error
                raise QueueParseException

        elif action == 'PORTOPEN':
            '''
            * Opens the valve of the specified port on the specified reactor.
            * Arguments
                1. Reactor ID
                2. Port number (1, 2, 3, or 4)
            '''
            rID = int(arg1)
            pnum = int(arg2)
            err = self.get_reactor_display(ID=rID).port_btns[pnum]['valve'].open_valve()
            if err == 1:
                # Error
                raise QueueParseException

        elif action == 'PORTCLOSE':
            '''
            * Closes the valve of the specified port on the specified reactor.
            * Arguments
                1. Reactor ID
                2. Port number (1, 2, 3, or 4)
            '''
            rID = int(arg1)
            pnum = int(arg2)
            err = self.get_reactor_display(ID=rID).port_btns[pnum]['valve'].close_valve()
            if err == 1:
                # Error
                raise QueueParseException

        elif action == 'OUTLETCLOSE':
            '''
            * Closes the outlet valve of the specified reactor
            * Arguments
                1. Reactor ID
            '''
            rID = int(arg1)
            err = self.get_reactor_display(ID=rID).outlet_btn.close_valve()
            if err == 1:
                # Error
                raise QueueParseException

        elif action == 'OUTLETOPEN':
            '''
            * Opens the outlet valve of the specified reactor
            * Arguments
                1. Reactor ID
            '''
            rID = int(arg1)
            err = self.get_reactor_display(ID=rID).outlet_btn.open_valve()
            if err == 1:
                # Error
                raise QueueParseException

        elif action == 'SEPCLOSE':
            '''
            * Closes the separator valve of the specified reactor
            * Arguments
                1. Reactor ID
            '''
            rID = int(arg1)
            err = self.get_reactor_display(ID=rID).sep_btn.close_valve()
            if err == 1:
                # Error
                raise QueueParseException

        elif action == 'SEPOPEN':
            '''
            * Opens the separator valve of the specified reactor
            * Arguments
                1. Reactor ID
            '''
            rID = int(arg1)
            err = self.get_reactor_display(ID=rID).sep_btn.open_valve()
            if err == 1:
                # Error
                raise QueueParseException

        elif action == 'JAWCLOSE':
            '''
            * Closes the jaw of the specified reactor bay
            * Arguments
                1. Reactor bay, in format `x y`
            '''
            x, y = arg1.split(' ')
            x = int(x)
            y = int(y)
            err = self.get_reactor_display(x, y).jaw_btn.close_valve()
            if err == 1:
                # Error
                raise QueueParseException

        elif action == 'JAWOPEN':
            '''
            * Opens the jaw of the specified reactor bay
            * Arguments
                1. Reactor bay, in format `x y`
            '''
            x, y = arg1.split(' ')
            x = int(x)
            y = int(y)
            err = self.get_reactor_display(x, y).jaw_btn.open_valve()
            if err == 1:
                # Error
                raise QueueParseException

        elif action == 'REACTORJAWCLOSE':
            '''
            * Same as `JAWCLOSE`, but takes in reactor ID as argument
            * Arguments
                1. Reactor ID
            '''
            rID = int(arg1)
            err = self.get_reactor_display(ID=rID).jaw_btn.close_valve()
            if err == 1:
                # Error
                raise QueueParseException

        elif action == 'REACTORJAWOPEN':
            '''
            * Same as `JAWOPEN`, but takes in reactor ID as argument
            * Arguments
                1. Reactor ID
            '''
            rID = int(arg1)
            err = self.get_reactor_display(ID=rID).jaw_btn.open_valve()
            if err == 1:
                # Error
                raise QueueParseException

        elif action == 'STACKCLOSE':
            '''
            * Closes (compresses) specified reactor stack
            * Arguments
                1. Stack number (same as `x` coordinate of reactor bays)
            '''
            x = int(arg1)
            err = self.get_stack_window(x).stack_btn.close_valve()
            if err == 1:
                # Error
                raise QueueParseException

        elif action == 'STACKOPEN':
            '''
            * Opens (decompresses) specified reactor stack
            * Arguments
                1. Stack number (same as `x` coordinate of reactor bays)
            '''
            x = int(arg1)
            err = self.get_stack_window(x).stack_btn.open_valve()
            if err == 1:
                # Error
                raise QueueParseException

        elif action == 'FITTINGCLOSE':
            '''
            * Closes fitting actuator of specified reactor stack
            * Arguments
                1. Stack number (same as `x` coordinate of reactor bays)
            '''
            x = int(arg1)
            err = self.get_stack_window(x).fitting_btn.close_valve()
            if err == 1:
                # Error
                raise QueueParseException

        elif action == 'FITTINGOPEN':
            '''
            * Opens fitting actuator of specified reactor stack
            * Arguments
                1. Stack number (same as `x` coordinate of reactor bays)
            '''
            x = int(arg1)
            err = self.get_stack_window(x).fitting_btn.open_valve()
            if err == 1:
                # Error
                raise QueueParseException

        elif action == 'BLECONNECT':
            '''
            * Connects via Bluetooth to specified reactor
            * Arguments
                1. Reactor ID
            '''
            rID = int(arg1)
            if not self.get_reactor_display(ID=rID).connected:
                self.get_reactor_display(ID=rID).on_connect_pressed(callback=self.resume)
                return 1
            else:
                self.cnsl_print('NOTE: Bluetooth already connected.')

        elif action == 'BLEDISCONNECT':
            '''
            * Disconnects via Bluetooth to specified reactor
            * Arguments
                1. Reactor ID
            '''
            rID = int(arg1)
            if self.get_reactor_display(ID=rID).connected:
                self.get_reactor_display(ID=rID).on_connect_pressed(callback=self.resume)
                return 1
            else:
                self.cnsl_print('NOTE: Bluetooth already disconnected.')

        elif action == 'TEMPNOTIFSON':
            '''
            * Turns on temperature notifications
            * Arguments
                1. Reactor ID
            '''
            
            # UNIMPLEMENTED
            self.cnsl_print('NOTE: TEMPNOTIFSON not yet implemented. Notifs are turned on by default.')

        elif action == 'TEMPNOTIFSOFF':
            '''
            * Turns off temperature notifications
            * Arguments
                1. Reactor ID
            '''
            
            # UNIMPLEMENTED
            self.cnsl_print('NOTE: TEMPNOTIFSOFF not yet implemented.')

        elif action == 'PRESSURENOTIFSON':
            '''
            * Turns on pressure notifications
            * Arguments
                1. Reactor ID
            '''
            
            # UNIMPLEMENTED
            self.cnsl_print('NOTE: PRESSURENOTIFSON not yet implemented. Notifs are turned on by default.')

        elif action == 'PRESSURENOTIFSOFF':
            '''
            * Turns off pressure notifications
            * Arguments
                1. Reactor ID
            '''
            
            # UNIMPLEMENTED
            self.cnsl_print('NOTE: PRESSURENOTIFSOFF not yet implemented.')

        elif action == 'SETPOINT':
            '''
            * Sets thermocontroller setpoint
            * Arguments
                1. Reactor ID
                2. Setpoint, integer between 0 and 255
            '''
            rID = int(arg1)
            sp = arg2
            self.get_reactor_display(ID=rID).sp_temp.delete(0, END)
            self.get_reactor_display(ID=rID).sp_temp.insert(0, sp)
            err = self.get_reactor_display(ID=rID).on_update_pressed()
            if err == 1:
                # Error
                raise QueueParseException

        elif action == 'TEMPCONTROLON':
            '''
            * Turns on thermocontroller
            * Arguments
                1. Reactor ID
            '''
            rID = int(arg1)

            # UNIMPLEMENTED
            self.cnsl_print('NOTE: TEMPCONTROLON not yet implemented. Control is automatically turned on when setting the setpoint.')

        elif action == 'TEMPCONTROLOFF':
            '''
            * Turns off thermocontroller
            * Arguments
                1. Reactor ID
            '''

            # This currently just sets the setpoint to 0
            self.cnsl_print('NOTE: TEMPCONTROLOFF currently just sets the setpoint to 0. To turn back on, call SETPOINT')
            rID = int(arg1)
            self.get_reactor_display(ID=rID).sp_temp.delete(0, END)
            self.get_reactor_display(ID=rID).sp_temp.insert(0, "0")
            err = self.get_reactor_display(ID=rID).on_update_pressed()
            if err == 1:
                # Error
                raise QueueParseException

        elif action == 'MIXINGSPEED':
            '''
            * Sets motor speed of specified reactor
            * Arguments
                1. Reactor ID
                2. Motor speed, integer from 0-100
            '''
            rID = int(arg1)
            speed = int(arg2)
            self.get_reactor_display(ID=rID).mixing.set(speed)
            err = self.get_reactor_display(ID=rID).on_mixing_change_done(None)
            if err == 1:
                # Error
                raise QueueParseException

        elif action == 'TIMEOUT':
            '''
            * Pauses for specified time
            * Arguments
                1. Timeout in milliseconds
            '''
            t = int(arg1)

            self.cnsl_print('Waiting %.3f seconds...' % (t/1000.))
            self.master.after(t, lambda:self.resume(None))
            return 1

        else:
            self.cnsl_print('Error - step %d: Action "%s" not recognized.' % (self.step, action))
            raise QueueParseException

        return 0




    # Callback used for operations that the program must wait for to finish.
    def resume(self, msg):

        try:

            # Finish the last task
            action = self.actions[-1]

            if action == 'REACTORMOVE':
                if msg == 1:
                    # Error
                    self.cnsl_print('Error - step %d: Robot couldn\'t complete move.' % self.step)
                    raise QueueParseException
                elif msg == 2:
                    # Internal error, which should already have been displayed on console
                    raise QueueParseException

            elif action == 'PUMPCONNECT' or action == 'PUMPDISCONNECT':
                if msg == 1:
                    # Error
                    self.cnsl_print('Error - step %d: Robot couldn\'t complete pipe move.' % self.step)
                    raise QueueParseException
                elif msg == 2:
                    # Internal error, which should already have been displayed on console
                    raise QueueParseException
            elif action == 'BLECONNECT' or action == 'BLEDISCONNECT':
                if msg > 0:
                    # Error
                    raise QueueParseException

            # Continue queueing where we left off
            self.process()

        except QueueParseException:
            self.cnsl_print('Exiting Queue Mode')
        except ValueError:
            self.cnsl_print('Error - step %d: Couldn\'t parse value.' % self.step)



    def get_stack_window(self, x):
        if x in self.stacks:
            return self.stacks[x]
        # Error
        self.cnsl_print('Error - step %d: Stack %d not found.' % (self.step, x))
        raise QueueParseException



    def get_reactor_display(self, x=None, y=None, ID=None):
        if ID is not None:
            if ID in self.reactors:
                return self.get_reactor_display(*self.reactors[ID])
            # Error
            self.cnsl_print('Error - step %d: Location of reactor %d not known. Make sure to call REACTORSETUP first.' % (self.step, ID))
            raise QueueParseException
        if x in self.stacks:
            if y in self.stacks[x].reactors:
                return self.stacks[x].reactors[y]
        # Error
        self.cnsl_print('Error - step %d: No such reactor position (%d,%d).' % (self.step, x, y))
        raise QueueParseException


    def get_reactor_type_from_id(self, id_):
        for rt in CFG['reactor types']:
            if  CFG['reactor types'][rt]['id'] == id_:
                return rt
        # Error
        self.cnsl_print('Error - step %d: Reactor with ID %d not found.' % (self.step, id_))
        raise QueueParseException



class QueueParseException(Exception):
    pass



