
from ble.client import Dongle as BleDongle
from pumps.sock import PumpController 
from valves.modbus import ValveController

# import robot_use

import sys
sys.path.insert(0, 'C:\Users\ROB\Dropbox\Robotic_Toolbox\Robot\UR3')



import threading
import time

from cfg import CFG

def hi():
	print 'hi'
	time.sleep(5)
	print 'hello'

class Controller:
	def __init__(self):
		self.pump_cbs = []

		self.pumps = None
		self.ble = None
		self.valves = None

	def valve_connect(self):
		self.valves = ValveController(host=CFG["festo_ip"])

	def valve_disconnect(self):
		if self.valves is not None:
			self.valves.stop()

	def ble_connect(self):
		self.ble = BleDongle(CFG["ble dongle port"])

	def ble_disconnect(self):
		pass

	# Calls all the callbacks added to the callback list
	def pump_callback(self, msg):
		print 'Pump message received: %s' % msg
		for pcb in self.pump_cbs:
			pcb(msg)

	def pumps_connect(self):
		self.pumps = PumpController(self.pump_callback, ip=CFG["pumps_ip"], port=CFG["pumps_port"])

	def pumps_disconnect(self):
		if self.pumps is not None:
			self.pumps.stop()

	def add_pump_callback(self, cb):
		self.pump_cbs.append(cb)

	## ROBOT FUNCTIONS ##
	def moveReactor(self, storeNum, bayNum, direction, reactorType = 'normal', between_stores = False, between_bays = False, verbose = None):
		print 'moving reactor'
		print storeNum, bayNum, direction, reactorType, between_stores, between_bays, verbose

		# Start thread
		# t = threading.Thread(target=robot_use.moveReactor, args = (storeNum, bayNum, direction, reactorType, between_stores, between_bays, verbose))
		# t.start()

	def movePipe(nearNum, farNum, direction, xDisp = .05, yDisp = .03):
		print 'moving pipe'
		print nearNum, farNum, direction, xDisp, yDisp

		# t = threading.Thread(target=robot_use.movePipe, args = (nearNum, farNum, direction, xDisp, yDisp))
		# t.start()