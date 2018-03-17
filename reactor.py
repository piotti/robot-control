from Tkinter import *
import tkMessageBox as messagebox

from cfg import CFG

from controller import *

import time

from ble.client import ble_decode

from graph import add_temp_set, add_pressure_set, TEMP_SETS, PRESSURE_SETS


class ValveButton:
	def __init__(self, c, cnsl, addr, *args, **kwargs):
		self.cnsl = cnsl

		if 'command' in kwargs:
			cb = self.make_cb(kwargs['command'])
			kwargs['command'] = cb
		else:
			cb = self.make_cb(lambda x:None)
			kwargs['command'] = cb

		

		self.c = c
		self.addr = int(addr)

		if self.addr == 0:
			kwargs['state'] = DISABLED

		self.btn = Button(*args, **kwargs)

		if self.addr != 0:
			self.read()
			print self.open	

		

	def read(self):
		self.open = self.c.valves.readValves()[self.addr-1]
		self.btn['bg'] = 'green' if self.open else Button().cget("background")

	def grid(self, *args, **kwargs):
		self.btn.grid(*args, **kwargs)
		
	def pack(self, *args, **kwargs):
		self.btn.pack(*args, **kwargs)

	# This routed the previous callback through this function
	def make_cb(self, prev_cb):
		def cb():
			self.cnsl('changing state of valve %d' % (self.addr-1))
			# Check state
			if self.open:
				# Close
				self.c.valves.closeValve(self.addr-1)
				time.sleep(.05)
				self.read()
			else:
				# Open
				self.c.valves.openValve(self.addr-1)
				time.sleep(.05)
				self.read()

			prev_cb()
		return cb



class ReactorDisplay:

	def __init__(self, master, idx, c, cnsl):
		self.master = master
		self.idx = idx
		self.c = c

		self.cnsl = cnsl

		self.connected = False

		self.timeout = 10
		self.time = self.timeout

		###   COLUMN 0   ###
		f0 = Frame(master)
		f0.grid(row=idx-1, column=0, padx=5, pady=1, sticky=N)
		# "Reactor: Jaw 1"
		ValveButton(c, cnsl, CFG['slots'][str(idx)]['jaw'], f0,
				text='Reactor\nJaw %d' % idx,
				command=self.on_jaw_close, height=7, width=10).pack()

		

		###   COLUMN 1   ###
		f1 = Frame(master)
		f1.grid(row=idx-1, column=1, padx=1, pady=1, sticky=N)
		# "Reactor Type"
		rf = Frame(f1, bd=2, relief='ridge')
		rf.grid(row=0, rowspan=2, column=0, padx=1, pady=5)
		Label(rf, text='Reactor Type:', height=1, width=12).grid(
			row=0, column=0, padx=1, pady=0, )
		self.reactor_type = StringVar(rf)
		self.reactor_type.set(sorted(CFG["reactor types"].keys())[0])
		OptionMenu(rf, self.reactor_type, *sorted(CFG["reactor types"].keys()), command=self.on_reactor_type_change).grid(
				row=2, column=0, padx=1, pady=0, ipadx=20)
		# 'Move to Storage', 'Move to Stack'
		mf = Frame(f1, bd=2, relief='ridge')
		mf.grid(row=2, column=0)
		Button(mf, text='To Storage', command=self.on_move_to_storage).grid(row=0, column=0)
		Button(mf, text='To Stack', command=self.on_move_to_stack).grid(row=0, column=1)
		# 'SP Temp'
		spf = Frame(f1, bd=2, relief='ridge')
		spf.grid(row=3, column=0)
		Label(spf, text='SP:',
				height=1, width=6).grid(
				row=0, column=0)
		self.sp_temp = Entry(spf, width=6)
		self.sp_temp.grid(row=0, column=1)



		###   COLUMN 2   ###
		f2 = Frame(master)
		f2.grid(row=idx-1, column=2, padx=1, pady=1, sticky=N)
		# 'Reactor Position'
		self.position = Label(f2, text='Position:\n%d'%CFG["reactor types"][self.reactor_type.get()]['position'],
				height=2, width=12, bd=2, relief='ridge')
		self.position.grid(row=0, rowspan=2, column=0, padx=1, pady=5)
		# 'BLE ID'
		self.ble_id = Label(f2, text='BLE ID:\n%s'% CFG["reactor types"][self.reactor_type.get()]['ble addr'],
				height=2, width=12, bd=2, relief='ridge')
		self.ble_id.grid(row=2, column=0, padx=1, pady=5)
		# 'Read ID'
		Button(f2, text='Read ID',
				height=1, width=12, command=self.on_read_ble_id).grid(
				row=4, rowspan=2, column=0, padx=1, pady=5, sticky=S)


		self.tube_numbers = {}
		self.flow_rates = {}
		self.pump_types = {}
		self.pump_ids = {}

		###   COLUMNS 3,4,5,6   ###
		for i in range(1, 5):
			f = Frame(master)
			f.grid(row=idx-1, column=2+i, padx=1, pady=1, sticky=N)
			# 'Port 1'
			pf = Frame(f, bd=2, relief='ridge')
			pf.grid(row=0, column=0, columnspan=2, padx=1, pady=5)
			Label(pf, text='Port %d' % i, height=1, width=6).grid(
				row=0, column=0, padx=1)
			Button(pf, text='Connect', command=self.make_port_connect_callback(i)).grid(
				row=0, column=1, padx=1)
			Button(pf, text='Disconnect', command=self.make_port_disconnect_callback(i)).grid(
				row=0, column=2, padx=1)
			# 'Tube #'
			tf = Frame(f, bd=2, relief='ridge')
			tf.grid(row=1, rowspan=2, column=0, padx=1, pady=5)
			Label(tf, text='Tube #', height=1, width=12).grid(
				row=0, column=0, padx=1, pady=0, )
			self.tube_numbers[i] = StringVar(tf)
			self.tube_numbers[i].set(" ") # default value
			OptionMenu(tf, self.tube_numbers[i], " ", *sorted(CFG['tubes'].keys()), command=self.make_tube_number_change_callback(i)).grid(
					row=2, column=0, padx=1, pady=0, ipadx=20)
			# 'Valve 1'
			ValveButton(c, cnsl, CFG['slots'][str(idx)]['valve %d' % i], f, text='Valve %d' % i,
					height=1, width=12, command=self.make_reactor_valve_callback(i)).grid(
					row=3, rowspan=1, column=0, padx=1, pady=5)
			# 'F Rate'
			frf = Frame(f, height=1, width=12, bd=2, relief='ridge')
			frf.grid(row=1, column=1, padx=1, pady=5)
			Label(frf, text='FR:',
					height=1, width=5).grid(
					row=1, column=1, padx=1, pady=0)
			self.flow_rates[i] = Entry(frf, width=6)
			self.flow_rates[i].grid(row=1, column=2, padx=1, pady=0)
			# 'P Rate'
			self.pump_types[i] = Label(f, text='P Type:', anchor=W,
					height=1, width=12, bd=2, relief='ridge')
			self.pump_types[i].grid(row=2, column=1, padx=1, pady=5)
			# 'P ID'
			self.pump_ids[i] = Label(f, text='P ID:', anchor=W,
					height=1, width=12, bd=2, relief='ridge')
			self.pump_ids[i].grid(row=3, column=1, padx=1, pady=5)
			# 'Start Pump'
			Button(f, text='Set Flow', command=self.make_start_pump_callback(i)).grid(
				row=4, column=0, padx=1, pady=0)
			# 'Stop Pump'
			Button(f, text='Stop Pump', command=self.make_stop_pump_callback(i)).grid(
				row=4, column=1, padx=1, pady=0)



		###   COLUMN 7   ###
		f7 = Frame(master)
		f7.grid(row=idx-1, column=7, padx=1, pady=1, sticky=N)
		# 'Outlet Valve'
		ValveButton(c, cnsl, CFG['slots'][str(idx)]['outlet'], f7, text='Outlet\nValve',
				height=2, width=8, command=self.on_outlet_valve_pressed).grid(
				row=0, column=1, padx=1, pady=5)
		# 'Sep Valve'
		ValveButton(c, cnsl, CFG['slots'][str(idx)]['sep'], f7, text='Sep\nValve',
				height=2, width=8, command=self.on_sep_valve_pressed).grid(
				row=1, column=1, padx=1, pady=5)



		###   COLUMN 8   ###
		f8 = Frame(master)
		f8.grid(row=idx-1, column=8, padx=1, pady=1, sticky=N)
		# 'BLE Data'
		Label(f8, text='BLE DATA',
					height=1, width=24, bd=2, relief='ridge').grid(
					row=0, column=0, columnspan=2, padx=1, pady=5, sticky=N)
		# 'Connect'
		self.connect_btn = Button(f8, text='Connect',
				height=1, width=10, command=self.on_connect_pressed)
		self.connect_btn.grid(row=1, column=0, padx=1, pady=0, sticky=W+N)
		# 'Update'
		Button(f8, text='Update',
				height=1, width=10, command=self.on_update_pressed).grid(
				row=2, column=0, padx=1, pady=0, sticky=W+N)
		# 'Mixing'
		self.mix_label = Label(f8, text='Mixing: 0%',
					height=1, width=10)
		self.mix_label.grid(row=3, column=0, padx=1, pady=0, sticky=N+W)
		self.mixing = Scale(f8, from_=0, to=100, orient=HORIZONTAL, command=self.on_mixing_change,
			showvalue=0, length=80)
		self.mixing.bind("<ButtonRelease-1>", self.on_mixing_change_done)
		self.mixing.grid(row=4, column=0, padx=1, pady=0, sticky=N+W)
		# 'Pressure'
		self.pressure = Label(f8, text='Pressure:',
					height=1, width=12, bd=2, relief='ridge', anchor=W)
		self.pressure.grid(row=1, column=1, padx=1, pady=5)
		# 'Temp'
		self.temp = Label(f8, text='Temp:',
					height=1, width=12, bd=2, relief='ridge', anchor=W)
		self.temp.grid(row=2, column=1, padx=1, pady=5)


	###   CALLBACKS ###
	def on_jaw_close(self):
		pass
		# self.cnsl( 'jaw close')
	def on_reactor_type_change(self, val):
		self.cnsl( val)
		self.cnsl( 'on_reactor_type_change')
		ble_addr = CFG['reactor types'][val]['ble addr']
		position = CFG['reactor types'][val]['position']
		self.ble_id['text'] = 'BLE ID:\n%s'% ble_addr
		self.position['text'] = 'Position:\n%d'% position

	def on_read_ble_id(self):
		self.cnsl( 'on_read_ble_id')
	def make_tube_number_change_callback(self, idx):
		def on_tube_number_change(val):
			self.cnsl( 'Port %s tube changed to %s' % (str(idx), str(val)))
			if val == ' ':
				# pump deslelected
				self.pump_types[idx]['text'] = 'P Type: '
				self.pump_ids[idx]['text'] = 'P ID: '
			else:
				self.pump_types[idx]['text'] = 'P Type: '+ str(CFG['tubes'][val]['type'])
				self.pump_ids[idx]['text'] = 'P ID: ' + str(CFG['tubes'][val]['ID'])
		return on_tube_number_change
	def make_reactor_valve_callback(self, idx):
		def on_reactor_valve_pressed():
			pass
			# self.cnsl( 'on_reactor_valve_pressed')
			# self.cnsl( idx)
		return on_reactor_valve_pressed
	def make_start_pump_callback(self, idx):
		def on_start_pump_pressed():
			fr = self.flow_rates[idx].get()
			self.cnsl( fr)
			try:
				fr = int(fr)
			except ValueError:
				self.cnsl( 'couldnt parse FR')
				return
			addr = self.pump_ids[idx]['text'][6:]
			self.cnsl( 'setting pump %s to flow rate %d' % (addr, fr))
			self.c.pumps.setFlow(addr, fr, CFG['tubes'][self.tube_numbers[idx].get()]['volume'])
		return on_start_pump_pressed
	def make_stop_pump_callback(self, idx):
		def on_stop_pump_pressed():
			addr = self.pump_ids[idx]['text'][6:]
			self.flow_rates[idx].delete(0, END)
			self.cnsl( 'stopping pump %s' % addr)
			self.c.pumps.stopFlow(addr)
		return on_stop_pump_pressed
	def on_outlet_valve_pressed(self):
		self.cnsl( 'on_outlet_valve_pressed')
	def on_sep_valve_pressed(self):
		self.cnsl( 'on_sep_valve_pressed')
	def on_connect_pressed(self):
		if not self.connected:
			addr = self.ble_id['text'][8:]
			self.cnsl( 'Connecting to PSOC ' + addr)

			# Show coutdown on connect button
			self.decrement_timer()
			# Start thread
			t = threading.Thread(target = self.connect_to_reactor, args = (addr,))
			t.start()
		else:
			addr = self.ble_id['text'][8:]
			self.cnsl( 'Disconnecting to PSOC ' + addr)
			self.c.ble.disconnect(self.connection.connection)
			self.connect_btn['text'] = 'Connect'
			self.connect_btn['bg'] = Button().cget("background")
			self.connected = False

	def on_update_pressed(self):
		if not self.connected:
			self.cnsl('Error: you are not connect to reactor')
			return
		val = self.sp_temp.get()
		try:
			self.connection.write(self.chars['ab29'].handle, val, 'int')
		except Exception:
			self.cnsl( 'Error when trying to set setpoint. Enter integer between 0 and 255')
			return
		self.cnsl( 'Setting setpoint to %s deg C' % val)
		


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
				if value < 30000:
					value = '%.2f' % (value/100)
				self.temp['text'] = 'Temp: %d' % value
			elif char.name == 'Pressure':
				self.pressure['text'] = 'Pressure: %d psi' % value

		return cb

	def on_mixing_change(self, val):
		self.mix_label['text'] = 'Mixing: '+val+'%'		

	def on_mixing_change_done(self, event):
		if not self.connected:
			self.mixing.set(0)
			self.cnsl('Error: you are not connect to reactor')
			return
		val = str(self.mixing.get())
		self.cnsl('Setting mixing at '+val+' %')
		self.connection.write(self.chars['1196'].handle, val, 'int')

	def on_move_to_storage(self):
		reactor = self.reactor_type.get()
		position = CFG['reactor types'][reactor]['position']
		bay = self.idx - 1
		self.cnsl('Moving reactor %s from bay slot %d to storage slot %d' % (reactor, bay, position))
		self.c.moveReactor(position, bay, -1)

	def on_move_to_stack(self):
		reactor = self.reactor_type.get()
		position = CFG['reactor types'][reactor]['position']
		bay = self.idx - 1
		self.cnsl('Moving reactor %s from storage slot %d to bay slot %d' % (reactor, position, bay))
		self.c.moveReactor(position, bay, 1)

	def make_port_connect_callback(self, idx):
		def cb():
			tube = self.tube_numbers[idx].get()
			if tube == ' ':
				self.cnsl('Error: No tube selected')
				return
			port = idx
			tower_num = CFG['slots'][str(self.idx)]["port %d" % port]
			if tower_num < 0:
				self.cnsl('Error: this port doesn\'t exist')
				return
			bay = self.idx - 1
			self.cnsl('Connecting tube %s to port %d of bay slot %d' % (tube, port, bay))
			self.c.movePipe(tower_num, int(tube), -1)
		return cb

	def make_port_disconnect_callback(self, idx):
		def cb():
			tube = self.tube_numbers[idx].get()
			if tube == ' ':
				self.cnsl('Error: No tube selected')
				return
			port = idx
			tower_num = CFG['slots'][str(self.idx)]["port %d" % port]
			if tower_num < 0:
				self.cnsl('Error: this port doesn\'t exist')
				return
			bay = self.idx - 1
			self.cnsl('Disconnecting tube %s from port %d of bay slot %d' % (tube, port, bay))
			self.c.movePipe(tower_num, int(tube), 1)
		return cb


	# THREADS
	def connect_to_reactor(self, addr):
		# Blocking function call:
		self.connection = self.c.ble.connect_to_reactor(addr)

		if self.connection is None:
			# Couldn't connect
			self.cnsl('Couldn\'t connect to ' + addr)
			self.connect_btn['text'] = 'Connect'
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