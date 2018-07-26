from Tkinter import *
from ttk import *
import ttk
import Tkinter
import Tkinter
import tkMessageBox as messagebox

from cfg import CFG

if CFG['test'] in ('True', 'true'):
	from test_controller import *
else:
	from controller import *


import time

# from ble.client import ble_decode

from graph import add_temp_set, add_pressure_set, TEMP_SETS, PRESSURE_SETS
from threadsafelabel import ThreadSafeLabel 


class ValveButton:
	def __init__(self, c, cnsl, addr, *args, **kwargs):
		self.cnsl = cnsl

		if 'command' in kwargs:
			cb = self.make_cb(kwargs['command'])
		else:
			cb = self.make_cb(lambda:None)

		self.cb = cb


		

		self.c = c
		self.festo = int(addr[0])
		self.addr = int(addr[1])

		if self.addr == -1:
			kwargs['state'] = DISABLED

		self.btn = Tkinter.Button(*args, **kwargs)
		self.btn.bind('<ButtonPress>', lambda _ : cb())


		if self.addr != -1:
			self.read()

		

	def read(self):
		# self.open = self.c.valves.readValves()[self.addr]
		self.open = self.c.valves.readValve(self.festo, self.addr)
		# import tkFont
		# helv = tkFont.Font(family='Helvetica', size=14)
		# style.configure('TButton', background='green')
		self.btn['background'] = 'green' if self.open else Tkinter.Button().cget("background")
		# self.btn.configure(background='green')
		# self.btn['font'] = 'green'
		# self.btn.configure(font=helv)
	def grid(self, *args, **kwargs):
		self.btn.grid(*args, **kwargs)
		return self
		
	def pack(self, *args, **kwargs):
		self.btn.pack(*args, **kwargs)
		return self

	def event_generate(self, *args, **kwargs):
		self.btn.event_generate(*args, **kwargs)

	def open_valve(self):
		self.read()
		if not self.open:
			return self.cb()
		return 0

	def close_valve(self):
		self.read()
		if self.open:
			return self.cb()
		return 0

	# This routed the previous callback through this function
	def make_cb(self, prev_cb):
		def cb():
			if self.addr == -1:
				# Valve not connected to port
				self.cnsl('Error: Valve not connected to Festo port', color='red')
				return 1
			self.cnsl('changing state of valve %d' % self.addr)
			# Check state
			if self.open:
				# Close
				self.c.valves.closeValve(self.festo, self.addr)
				time.sleep(.05)
				self.read()
			else:
				# Open
				self.c.valves.openValve(self.festo, self.addr)
				time.sleep(.05)
				self.read()

			return prev_cb()
		return cb

class Button:
	def __init__(self, *args, **kwargs):
		cb = kwargs.get('command', lambda:None)
		if 'command' in kwargs:
			del kwargs['command']
		if kwargs.get('tk', False):
			del kwargs['tk']
			self.btn = Tkinter.Button(*args, **kwargs)
		else:
			if 'tk' in kwargs:
				del kwargs['tk']
			self.btn = ttk.Button(*args, **kwargs)
		

		self.btn.bind('<ButtonPress>', lambda _ : cb())

	def grid(self, *args, **kwargs):
		self.btn.grid(*args, **kwargs)
		return self
		
	def pack(self, *args, **kwargs):
		self.btn.pack(*args, **kwargs)
		return self
	def event_generate(self, *args, **kwargs):
		self.btn.event_generate(*args, **kwargs)

	def __setitem__(self, *args):
		self.btn.__setitem__(*args)



class ReactorDisplay:

	def __init__(self, master, idx, name, c, cnsl, stack_idx, graph):
		self.master = master
		self.idx = idx
		self.name = name
		self.c = c
		self.stack_idx = stack_idx
		self.graph = graph

		self.cnsl = cnsl

		self.connected = False

		self.timeout = 10
		self.time = self.timeout

		# Create data series objects for pressure and temp graphing
		self.temp_set = None
		self.pressure_set = None

		###   COLUMN 0   ###
		f0 = Frame(master)
		f0.grid(row=idx, column=0, padx=5, pady=1, sticky=N)
		# "Reactor: Jaw 1"
		self.jaw_btn = ValveButton(c, cnsl, CFG['slots'][str(name)]['jaw'], f0,
				text='Reactor Jaw %d' % idx,
				command=self.on_jaw_close,  width=15, height=6).pack(fill=BOTH)

		

		###   COLUMN 1   ###
		f1 = Frame(master)
		f1.grid(row=idx, column=1, padx=1, pady=1, sticky=N)
		# "Reactor Type"
		rf = Frame(f1, borderwidth=2, relief='ridge')
		rf.grid(row=0, rowspan=2, column=0, padx=1, pady=5)
		Label(rf, text='Reactor Type:',  width=24).grid(
			row=0, column=0, padx=1, pady=0, )
		self.reactor_type = StringVar(rf)
		# self.reactor_type.set(sorted(CFG["reactor types"].keys())[0])
		self.reactor_type.set('')
		options = [' '] + sorted(CFG["reactor types"].keys())
		OptionMenu(rf, self.reactor_type, *options, command=self.on_reactor_type_change).grid(
				row=2, column=0, padx=1, pady=0, ipadx=20)
		# 'Move to Storage', 'Move to Stack'
		mf = Frame(f1, borderwidth=2, relief='ridge')
		mf.grid(row=2, column=0)
		self.storage_btn = Button(mf, text='To Storage', command=self.on_move_to_storage).grid(row=0, column=0)
		self.stack_btn = Button(mf, text='To Stack', command=self.on_move_to_stack).grid(row=0, column=1)
		# 'SP Temp'
		spf = Frame(f1, borderwidth=2, relief='ridge')
		spf.grid(row=3, column=0)
		Label(spf, text='Setpoint:', justify='center',
				 width=12).grid(
				row=0, column=0)
		self.sp_temp = Entry(spf, width=12)
		self.sp_temp.grid(row=0, column=1)



		###   COLUMN 2   ###
		f2 = Frame(master)
		f2.grid(row=idx, column=2, padx=1, pady=1, sticky=N)
		# 'Reactor Position'
		# self.position = Label(f2, text='Storage Position:\n%s'% str((CFG["reactor types"][self.reactor_type.get()]['storage x'],CFG["reactor types"][self.reactor_type.get()]['storage y'])),
				 # width=20, borderwidth=2, relief='ridge')
		self.position = Label(f2, text='Storage Position:\n',
				 width=20, borderwidth=2, relief='ridge')
		self.position.grid(row=0, rowspan=2, column=0, padx=1, pady=5)
		# 'BLE ID'
		# self.ble_id = Label(f2, text='BLE ID:\n%s'% CFG["reactor types"][self.reactor_type.get()]['ble addr'],
		# 		 width=20, borderwidth=2, relief='ridge')
		self.ble_id = Label(f2, text='BLE ID:\n',
				 width=20, borderwidth=2, relief='ridge')
		self.ble_id.grid(row=2, column=0, padx=1, pady=5)
		# 'Read ID'
		self.read_id_btn = Button(f2, text='Read ID',
				 width=20, command=self.on_read_ble_id).grid(
				row=4, rowspan=2, column=0, padx=1, pady=5, sticky=S)


		self.tube_numbers = {}
		self.flow_rates = {}
		self.pump_types = {}
		self.pump_ids = {}

		self.port_btns = {}
		###   COLUMNS 3,4,5,6   ###
		for i in range(1, 5):
			self.port_btns[i] = {}

			f = Frame(master)
			f.grid(row=idx+1, column=2+i-3, padx=1, pady=1, sticky=N)
			# 'Port 1'
			state = NORMAL if int(CFG['slots'][str(name)]['port %d' % i][1]) >= 0 else DISABLED
			pf = Frame(f, borderwidth=2, relief='ridge')
			pf.grid(row=0, column=0, columnspan=2, padx=1, pady=5)
			Label(pf, text='Port %d' % i,  width=6).grid(
				row=0, column=0, padx=1)
			self.port_btns[i]['connect'] = Button(pf, text='Connect', command=self.make_port_connect_callback(i) if state==NORMAL else lambda:None, state=state).grid(
				row=0, column=1, padx=1)
			self.port_btns[i]['disconnect'] = Button(pf, text='Disconnect', command=self.make_port_disconnect_callback(i) if state==NORMAL else lambda:None, state=state).grid(
				row=0, column=2, padx=1)
			# 'Tube #'
			tf = Frame(f, borderwidth=2, relief='ridge')
			tf.grid(row=1, rowspan=2, column=0, padx=1, pady=5)
			Label(tf, text='Tube #',  width=12).grid(
				row=0, column=0, padx=1, pady=0, )
			self.tube_numbers[i] = StringVar(tf)
			self.tube_numbers[i].set(" ") # default value
			OptionMenu(tf, self.tube_numbers[i], " ", *sorted(CFG['tubes'].keys()), command=self.make_tube_number_change_callback(i)).grid(
					row=2, column=0, padx=1, pady=0, ipadx=20)
			# 'Valve 1'
			self.port_btns[i]['valve'] = ValveButton(c, cnsl, CFG['slots'][str(name)]['valve %d' % i], f, text='Valve %d' % i,
					 width=12, command=self.make_reactor_valve_callback(i)).grid(
					row=3, rowspan=1, column=0, padx=1, pady=5)
			# 'F Rate'
			frf = Frame(f,  width=12, borderwidth=2, relief='ridge')
			frf.grid(row=1, column=1, padx=1, pady=5)
			Label(frf, text='FR:',
					 width=5).grid(
					row=1, column=1, padx=1, pady=0)
			self.flow_rates[i] = Entry(frf, width=6)
			self.flow_rates[i].grid(row=1, column=2, padx=1, pady=0)
			# 'P Rate'
			self.pump_types[i] = Label(f, text='', anchor=W,
					 width=12, borderwidth=2, relief='ridge')
			self.pump_types[i].grid(row=2, column=1, padx=1, pady=5)
			# 'P ID'
			self.pump_ids[i] = Label(f, text='P ID:', anchor=W,
					 width=12, borderwidth=2, relief='ridge')
			self.pump_ids[i].grid(row=3, column=1, padx=1, pady=5)
			# 'Start Pump'
			self.port_btns[i]['start_pump'] = Button(f, text='Set Flow', command=self.make_start_pump_callback(i)).grid(
				row=4, column=0, padx=1, pady=0)
			# 'Stop Pump'
			self.port_btns[i]['stop_pump'] = Button(f, text='Stop Pump', command=self.make_stop_pump_callback(i)).grid(
				row=4, column=1, padx=1, pady=0)



		###   COLUMN 7   ###
		f78 = Frame(master)
		f78.grid(row=idx, column=7-4, padx=1, pady=1, sticky=N)

		f7 = Frame(f78)
		f7.grid(row=0, column=0)
		# f7.grid(row=idx, column=7-4, padx=1, pady=1, sticky=N)
		# 'Outlet Valve'
		self.outlet_btn = ValveButton(c, cnsl, CFG['slots'][str(name)]['outlet'], f7, text='Outlet\nValve',
				 width=8, height=3, command=self.on_outlet_valve_pressed).grid(
				row=0, column=1, padx=1)
		# 'Sep Valve'
		self.sep_btn = ValveButton(c, cnsl, CFG['slots'][str(name)]['sep'], f7, text='Sep\nValve',
				 width=8, height=3, command=self.on_sep_valve_pressed).grid(
				row=1, column=1, padx=1)



		###   COLUMN 8   ###
		f8 = Frame(f78)
		# f8.grid(row=idx, column=8-4, padx=1, pady=1, sticky=N)
		f8.grid(row=0, column=1)
		# 'BLE Data'
		Label(f8, text='BLE DATA',
					 width=24, borderwidth=2, relief='ridge').grid(
					row=0, column=0, columnspan=2, padx=1, pady=5, sticky=N)
		# 'Connect'
		self.connect_btn = Button(f8, text='Connect',
				 width=10, command=self.on_connect_pressed, tk=True).grid(
				 row=1, column=0, padx=1, pady=0, sticky=W+N)
		# 'Update'
		self.update_btn = Button(f8, text='Update',
				 width=10, command=self.on_update_pressed).grid(
				row=2, column=0, padx=1, pady=0, sticky=W+N)
		# 'Mixing'
		self.mix_label = Label(f8, text='Mixing: 0%',
					 width=11)
		self.mix_label.grid(row=3, column=0, padx=1, pady=0, sticky=N+W)
		self.mixing = Scale(f8, from_=0, to=100, orient=HORIZONTAL, command=self.on_mixing_change,
			length=80)
		self.mixing.bind("<ButtonRelease-1>", self.on_mixing_change_done)
		self.mixing.grid(row=4, column=0, padx=1, pady=0, sticky=N+W)
		# 'Pressure'
		self.pressure = ThreadSafeLabel(f8, text='Press:',
					 width=12, borderwidth=2, relief='ridge', anchor=W)
		self.pressure.grid(row=1, column=1, padx=1, pady=5)
		# 'Temp'
		self.temp = ThreadSafeLabel(f8, text='Temp:',
					 width=12, borderwidth=2, relief='ridge', anchor=W)
		self.temp.grid(row=2, column=1, padx=1, pady=5)




		# self.reactor_type.trace('w', lambda *args: self.on_reactor_type_change())
		


	###   CALLBACKS ###
	def on_jaw_close(self):
		pass
		# self.cnsl( 'jaw close')
	def on_reactor_type_change(self, val):
		self.reactor_type.set(val)
		self.cnsl( 'on_reactor_type_change: %s' % val)
		ble_addr = CFG['reactor types'][val]['ble addr']
		position = CFG['reactor types'][val]['storage x'], CFG['reactor types'][val]['storage y']
		print position
		self.ble_id['text'] = 'BLE ID:\n%s'% ble_addr
		self.position['text'] = 'Storage Position:\n%s'% str(position)

		# Update graphing display name
		self.graph.set_reactor_name(self.name, self.reactor_type.get())

	def on_read_ble_id(self):
		self.cnsl( 'on_read_ble_id')
	def make_tube_number_change_callback(self, idx):
		def on_tube_number_change(val):
			self.tube_numbers[idx].set(val)
			self.cnsl( 'Port %s tube changed to %s' % (str(idx), str(val)))

			if val == ' ':
				# pump deslelected
				self.pump_types[idx]['text'] = ''
				self.pump_ids[idx]['text'] = 'P ID: '
			else:
				self.pump_types[idx]['text'] = ''+ str(CFG['tubes'][val]['type'])
				self.pump_ids[idx]['text'] = 'P ID: ' + str(CFG['tubes'][val]['ID'])
		return on_tube_number_change
	def make_reactor_valve_callback(self, idx):
		def on_reactor_valve_pressed():
			self.cnsl('on_reactor_valve_pressed')
			self.cnsl(idx)
		return on_reactor_valve_pressed
	def make_start_pump_callback(self, idx):
		def on_start_pump_pressed():
			fr = self.flow_rates[idx].get()
			self.cnsl( fr)
			try:
				fr = float(fr)
			except ValueError:
				self.cnsl( 'couldnt parse FR')
				return 1
			tube_num = self.tube_numbers[idx].get()
			self.cnsl( 'setting pump %s to flow rate %d' % (tube_num, fr))
			self.c.pumps.setFlow(tube_num, fr)
			return 0
		return on_start_pump_pressed
	def make_stop_pump_callback(self, idx):
		def on_stop_pump_pressed():
			addr = self.pump_ids[idx]['text'][6:]
			self.flow_rates[idx].delete(0, END)
			tube_num = self.tube_numbers[idx].get()
			self.cnsl( 'stopping pump %s' % tube_num)
			self.c.pumps.stopFlow(tube_num)
		return on_stop_pump_pressed
	def on_outlet_valve_pressed(self):
		self.cnsl( 'on_outlet_valve_pressed')
	def on_sep_valve_pressed(self):
		self.cnsl( 'on_sep_valve_pressed')
	def on_connect_pressed(self, callback = lambda x : None):
		if not self.connected:
			if self.reactor_type.get() == ' ':
				self.cnsl('Error: no reactor chosen.')
				return callback(2)

			addr = self.ble_id['text'][8:]
			self.cnsl( 'Connecting to PSOC ' + addr)

			# Show coutdown on connect button
			self.decrement_timer()
			# Start thread
			t = threading.Thread(target = self.connect_to_reactor, args = (addr,callback))
			t.start()
		else:
			addr = self.ble_id['text'][8:]
			self.cnsl( 'Disconnecting to PSOC ' + addr)
			self.c.ble.disconnect(self.connection.connection)
			self.connect_btn['text'] = 'Connect'
			self.connect_btn['bg'] = Tkinter.Button().cget("background")
			self.connected = False

	def on_update_pressed(self):
		if not self.connected:
			self.cnsl('Error: you are not connect to reactor')
			return 1
		val = self.sp_temp.get()
		print 'value:', val
		try:
			# Write setpoint
			self.connection.write(self.chars['ab29'].handle, val, 'int')

			time.sleep(0.5)

			# Write temp control on/off
			if int(val) == 0:
				self.connection.write(self.chars['6a65'].handle, 0, 'int')
			else:
				self.connection.write(self.chars['6a65'].handle, 1, 'int')


		except Exception as e:
			print e
			self.cnsl( 'Error when trying to set setpoint. Enter integer between 0 and 255')
			return 1
		self.cnsl( 'Setting setpoint to %s deg C' % val)
		return 0
		


	def make_write_event_callback(self, char):
		def cb(value):
			value = ble_decode(value, msbf=False)
			if char.type == 'int':
				value = int(value, 16)
			elif char.type == 'text':
				value = value.decode('hex')
			self.cnsl('MSG RECEIVE: %s --- %s' % (char.name, str(value)))

			# Write to screen to pertinent fields
			if char.name == 'Temperature':
				print 'temp', value, type(value)
				if value < 30000:
					value /= 100.
				#self.temp['text'] = 'Temp: %.2f' % value
				self.temp.set_text('Temp: %.2f' % value)
				print 'set temp'
				# Update graph
				if self.temp_set is None:
					print 'creating'
					self.temp_set = add_temp_set(self.name)
					print 'done creating'
				self.temp_set.add(value)
				print 'added'
			elif char.name == 'Pressure':
				#self.pressure['text'] = 'Press: %d psi' % value
				self.pressure.set_text('Press: %d psi' % value)
				# Update graph
				if self.pressure_set is None:
					self.pressure_set = add_pressure_set(self.name)
				self.pressure_set.add(value)

		return cb

	def on_mixing_change(self, val):
		val = str(int(float(val)))
		self.mix_label['text'] = 'Mixing: '+val+'%'		

	def on_mixing_change_done(self, event):
		if not self.connected:
			self.mixing.set(0)
			self.cnsl('Error: you are not connect to reactor')
			return 1
		val = int(self.mixing.get())
		self.cnsl('Setting mixing at '+str(val)+' %')
		self.connection.write(self.chars['1196'].handle, val, 'int')
		return 0

	def on_move_to_storage(self, callback=None):
		reactor = self.reactor_type.get()
		# position = CFG['reactor types'][reactor]['position']
		if reactor == ' ':
			self.cnsl('Error: no reactor chosen.')
			if callback is not None:
				return callback(2)
			else:
				return 

		position = (int(CFG['reactor types'][reactor]['storage x']), int(CFG['reactor types'][reactor]['storage y']))
		# bay = self.idx - 1
		bay = (int(self.stack_idx), int(self.idx))
		# bay = (CFG['stacks']['stack %d' % self.stack_idx]['x pos'], CFG['slots'][str(self.idx)]['y pos'])
		self.cnsl('Moving reactor %s from bay slot %s to storage lsot %s' % (reactor, str(bay), str(position)))
		self.c.moveReactor(position, bay, -1, reactorType=CFG['reactor types'][reactor]['type'], callback=callback)

	def on_move_to_stack(self, callback=None):
		reactor = self.reactor_type.get()

		if reactor == ' ':
			self.cnsl('Error: no reactor chosen.')
			if callback is not None:
				return callback(2)
			else:
				return 

		# position = CFG['reactor types'][reactor]['position']
		position = (int(CFG['reactor types'][reactor]['storage x']), int(CFG['reactor types'][reactor]['storage y']))
		# bay = self.idx - 1
		# bay = (CFG['stacks']['stack %d' % self.stack_idx]['x pos'], CFG['slots'][str(self.idx)]['y pos'])
		bay = (int(self.stack_idx), int(self.idx))
		self.cnsl('Moving reactor %s from storage slot %s to bay slot %s' % (reactor, str(position), str(bay)))
		self.c.moveReactor(position, bay, 1, reactorType=CFG['reactor types'][reactor]['type'], callback=callback)

	def make_port_connect_callback(self, idx):
		def cb(callback=None):
			tube = self.tube_numbers[idx].get()
			if tube == ' ':
				self.cnsl('Error: No tube selected')
				# Report error to queueing callback
				if callback is not None:
					callback(2)
				return
			# parse tube tuple
			tube = tuple(int(e) for e in tube.split(','))
			port = idx
			tower_num_cfg = CFG['slots'][str(self.name)]["port %d" % port]
			tower_num = int(tower_num_cfg[0]), int(tower_num_cfg[1])
			if tower_num[1] < 0:
				self.cnsl('Error: this port doesn\'t exist')
				return
			bay = self.idx
			self.cnsl('Connecting tube %s to port %d of bay slot %d' % (tube, port, bay))
			self.c.movePipe(tower_num, tube, -1, callback=callback)
		return cb

	def make_port_disconnect_callback(self, idx):
		def cb(callback=None):
			tube = self.tube_numbers[idx].get()
			if tube == ' ':
				self.cnsl('Error: No tube selected')
				# Report error to queueing callback
				if callback is not None:
					callback(2) 
				return
			# parse tube tuple
			tube = tuple(int(e) for e in tube.split(','))
			port = idx
			tower_num_cfg = CFG['slots'][str(self.name)]["port %d" % port]
			tower_num = int(tower_num_cfg[0]), int(tower_num_cfg[1])
			if tower_num[1] < 0:
				self.cnsl('Error: this port doesn\'t exist')
				return
			bay = self.idx
			self.cnsl('Disconnecting tube %s from port %d of bay slot %d' % (tube, port, bay))
			self.c.movePipe(tower_num, tube, 1, callback=callback)
		return cb


	# THREADS
	def connect_to_reactor(self, addr, callback):
		# Blocking function call:
		self.connection = self.c.ble.connect_to_reactor(addr)

		if self.connection is None:
			# Couldn't connect
			self.cnsl('Couldn\'t connect to ' + addr)
			self.connect_btn['text'] = 'Connect'
			self.connect_btn['bg'] = Tkinter.Button().cget("background")

			callback(1)
			return

		

		self.cnsl( 'Connection to ' + addr + ' established')

		# Read charachteristics
		self.chars = self.connection.get_characteristics()
		self.cnsl('Found charachteristics:' + ', '.join([e.name for e in self.chars.values()]))

		# Register callbacks and notifs
		for e in self.chars.values():
			self.connection.connection.assign_attrclient_value_callback(e.handle+1, self.make_write_event_callback(e))
			# Turn on notifs for notify characteristics
			if e.has_notify:
				self.connection.connection.characteristic_subscription(e.char, False, True)

		self.connect_btn['text'] = 'Disconnect'
		self.connect_btn['bg'] = 'green'
		self.connected = True
		callback(0)



	def decrement_timer(self):
		if self.time > 0:
			self.time -= 1

			# Update display
			self.connect_btn['text'] = 'Connecting: ' + str(self.time)

			# Recurse
			self.master.after(1000, self.decrement_timer)

			
		else:
			# reset timer
			self.time = self.timeout