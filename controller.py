
from ble.client import Dongle as BleDongle
from ble.client import ble_decode as bled
from pumps.pump_controller import PumpController
from pressure.alicat import PressureController 
from valves.modbus import ValveController

import nidaq

from cfg import CFG



import sys
sys.path.insert(0, 'C:\Users\ROB\Dropbox\Robotic_Toolbox\Robot\UR3')

if CFG['UR3'] in ('True', 'true'):
	import robot_use


import threading
import time


def ble_decode(value, msbf=False):
	return bled(value, msbf)


class Controller:
	def __init__(self, cnsl_print):

		self.cnsl_print = cnsl_print

		self.pump_cbs = []
		self.pressure_cbs = []

		self.pumps = None
		self.ble = None
		self.valves = None
		self.pressure = None


	def pressure_connect(self):
		self.pressure = PressureController(self.pressure_callback, ip=CFG['pressure controller ip'], port=int(CFG['pressure controller port']))

	def pressure_disconnect(self):
		if self.pressure is not None:
			self.pressure.close()

	def pressure_callback(self, msg):
		print 'Pressure message received: %s' % msg
		for pcb in self.pressure_cbs:
			pcb(msg)

	def valve_connect(self):
		hosts = CFG["festo 1 ip"],# CFG["festo 2 ip"]valves, CFG["festo 3 ip"]
		self.valves = ValveController(hosts)

	def valve_disconnect(self):
		if self.valves is not None:
			self.valves.stop()

	def ble_connect(self):
		self.ble = BleDongle(CFG["ble dongle port"])

	def ble_disconnect(self):
		pass

	def read_pressure():
		return nidaq.read_pressure()

	# Calls all the callbacks added to the callback list
	def pump_callback(self, msg):
		print 'Pump message received: %s' % msg
		for pcb in self.pump_cbs:
			pcb(msg)

	def pumps_connect(self):
		self.pumps = PumpController(self.pump_callback, CFG)

	def pumps_disconnect(self):
		if self.pumps is not None:
			self.pumps.stop()

	def add_pump_callback(self, cb):
		self.pump_cbs.append(cb)

	def add_pressure_callback(self, cb):
		self.pressure_cbs.append(cb)

	## ROBOT FUNCTIONS ##
	def moveReactor(self, storeNum, bayNum, direction, reactorType = 'normal', between_stores = False,
		between_bays = False, verbose = None, callback=None):

		def default_cb(err):
			if err == 0:
				self.cnsl_print('Reactor successfully moved')
			else:
				self.cnsl_print('Error: Robot failed to move reactor', color='red')
		if callback is None:
			callback = default_cb

		print 'moving reactor'
		print storeNum, bayNum, direction, reactorType, between_stores, between_bays, verbose
		storeNum = storeNum
		direction = int(direction)
		bayNum = bayNum


		# Start thread
		t = threading.Thread(target=move_reactor_thread, args = (storeNum, bayNum, direction, reactorType, callback))
		t.start()

	def movePipe(self, nearNum, farNum, direction, callback=None):

		def default_cb(err):
			if err == 0:
				self.cnsl_print('Pipe successfully moved')
			else:
				self.cnsl_print('Error: Robot failed to move pipe', color='red')
		if callback is None:
			callback = default_cb


		print 'moving pipe'
		print nearNum, farNum, direction
		nearNum = int(nearNum)
		nfarum = int(farNum)
		direction = int(direction)

		# Start motors
		nidaq.start()

		t = threading.Thread(target=move_pipe_thread, args = (nearNum, farNum, direction, callback))
		t.start()



def move_reactor_thread(storeNum, bayNum, direction, reactorType, callback):
	if robot_use.moveReactor(storeNum, bayNum, direction, reactorType):
		callback(0)
	else:
		callback(1)


def move_pipe_thread(nearNum, farNum, direction, callback):
	result = robot_use.movePipe(nearNum, farNum, direction)

	# Stop motors
	nidaq.stop()

	if result:
		callback(0)
	else:
		callback(1)