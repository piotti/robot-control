from Tkinter import *
import tkMessageBox as messagebox

# from ble.client import Dongle as BleDongle
# from pumps.sock import PumpController 
# from valves.modbus import ValveController



from cfg import CFG


class ValveButton:
	def __init__(self, *args, **kwargs):

		if 'command' in kwargs:
			cb = self.make_cb(kwargs['command'])
			kwargs['command'] = cb

		self.btn = Button(*args, **kwargs)

		self.open = False


	def grid(self, *args, **kwargs):
		self.btn.grid(*args, **kwargs)
		
	def pack(self, *args, **kwargs):
		self.btn.pack(*args, **kwargs)

	# This routed the previous callback through this function
	def make_cb(self, prev_cb):
		def cb():
			# Check state
			prev_cb()
		return cb



class ReactorDisplay:

	def __init__(self, master, idx):
		self.master = master
		self.idx = idx

		self.connected = False

		###   COLUMN 0   ###
		f0 = Frame(master)
		f0.grid(row=idx-1, column=0, padx=5, pady=1, sticky=N)
		# "Reactor: Jaw 1"
		ValveButton(f0, text='Reactor\nJaw %d' % idx, command=self.on_jaw_close,
				height=7, width=10).pack()

		

		###   COLUMN 1   ###
		f1 = Frame(master)
		f1.grid(row=idx-1, column=1, padx=1, pady=1, sticky=N)
		# "Reactor Type"
		rf = Frame(f1, bd=2, relief='ridge')
		rf.grid(row=0, rowspan=2, column=0, padx=1, pady=5)
		Label(rf, text='Reactor Type:', height=1, width=12).grid(
			row=0, column=0, padx=1, pady=0, )
		self.reactor_type = StringVar(rf)
		self.reactor_type.set(CFG["reactor types"][0])
		OptionMenu(rf, self.reactor_type, *CFG["reactor types"], command=self.on_reactor_type_change).grid(
				row=2, column=0, padx=1, pady=0, ipadx=20)
		# 'SP Temp'
		Label(f1, text='Setpoint temp:',
				height=1, width=12).grid(
				row=2, column=0)
		self.sp_temp = Entry(f1, text='Setpoint Temp',
				width=12)
		self.sp_temp.grid(row=3, column=0)



		###   COLUMN 2   ###
		f2 = Frame(master)
		f2.grid(row=idx-1, column=2, padx=1, pady=1, sticky=N)
		# 'Reactor Position'
		self.position = Label(f2, text='Position:\n3',
				height=2, width=12, bd=2, relief='ridge')
		self.position.grid(row=0, rowspan=2, column=0, padx=1, pady=5)
		# 'BLE ID'
		self.ble_id = Label(f2, text='BLE ID:\nA98EC2C3',
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
			Label(f, text='Port %d' % i,
					height=1, width=26, bd=2, relief='ridge').grid(
					row=0, column=0, columnspan=2, padx=1, pady=5)
			# 'Tube #'
			tf = Frame(f, bd=2, relief='ridge')
			tf.grid(row=1, rowspan=2, column=0, padx=1, pady=5)
			Label(tf, text='Tube #', height=1, width=12).grid(
				row=0, column=0, padx=1, pady=0, )
			self.tube_numbers[i] = StringVar(tf)
			self.tube_numbers[i].set("1") # default value
			OptionMenu(tf, self.tube_numbers[i], "1", "2", "3", command=self.make_tube_number_change_callback(i)).grid(
					row=2, column=0, padx=1, pady=0, ipadx=20)
			# 'Valve 1'
			ValveButton(f, text='Valve %d' % i,
					height=1, width=12, command=self.make_reactor_valve_callback(i)).grid(
					row=3, rowspan=2, column=0, padx=1, pady=5)
			# 'F Rate'
			frf = Frame(f, height=1, width=12, bd=2, relief='ridge')
			frf.grid(row=1, column=1, padx=1, pady=5)
			Label(frf, text='FR:',
					height=1, width=5).grid(
					row=1, column=1, padx=1, pady=0)
			self.flow_rates[i] = Entry(frf, width=5)
			self.flow_rates[i].grid(row=1, column=2, padx=1, pady=0)
			# 'P Rate'
			self.pump_types[i] = Label(f, text='P Type:', anchor=W,
					height=1, width=12, bd=2, relief='ridge')
			self.pump_types[i].grid(row=2, column=1, padx=1, pady=5)
			# 'P ID'
			self.pump_ids[i] = Label(f, text='P ID:', anchor=W,
					height=1, width=12, bd=2, relief='ridge')
			self.pump_ids[i].grid(row=3, column=1, padx=1, pady=5)



		###   COLUMN 7   ###
		f7 = Frame(master)
		f7.grid(row=idx-1, column=7, padx=1, pady=1, sticky=N)
		# 'Outlet Valve'
		ValveButton(f7, text='Outlet\nValve',
				height=2, width=8, command=self.on_outlet_valve_pressed).grid(
				row=0, column=1, padx=1, pady=5)
		# 'Sep Valve'
		ValveButton(f7, text='Sep\nValve',
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
		Label(f8, text='Mixing: 30%',
					height=1, width=10).grid(
					row=3, column=0, padx=1, pady=0, sticky=N+W)
		self.mixing = Scale(f8, from_=0, to=100, orient=HORIZONTAL, showvalue=0, length=80)
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
		print 'jaw close'
	def on_reactor_type_change(self, val):
		print val
		print 'on_reactor_type_change'
	def on_read_ble_id(self):
		print 'on_read_ble_id'
	def make_tube_number_change_callback(self, idx):
		def on_tube_number_change(val):
			print 'on_tube_number_change'
			print idx
			print val
		return on_tube_number_change
	def make_reactor_valve_callback(self, idx):
		def on_reactor_valve_pressed():
			print 'on_reactor_valve_pressed'
			print idx
		return on_reactor_valve_pressed
	def on_outlet_valve_pressed(self):
		print 'on_outlet_valve_pressed'
	def on_sep_valve_pressed(self):
		print 'on_sep_valve_pressed'
	def on_connect_pressed(self):
		print 'on_connect_pressed'
	def on_update_pressed(self):
		print 'on_update_pressed'