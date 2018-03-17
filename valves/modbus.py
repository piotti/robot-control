import traceback
import time
from pymodbus.client.sync import ModbusTcpClient as ModbusClient


class ValveController:
	def __init__(self, host='192.168.1.6'):
		print 'connecting to Festo...'
		self.client = ModbusClient(host=host)
		if not self.client.connect():
			print('Couldn\'t connect')

		self.closeAll()

	def closeAll(self):
		for i in range(16):
			self.client.write_coil(i, False)

	def openAll(self):
		for i in range(16):
			self.client.write_coil(i, True)

	def openValve(self, valve):
		self.client.write_coil(valve, True)

	def closeValve(self, valve):
		self.client.write_coil(valve, False)

	def writeValve(self, valve, state):
		self.client.write_coil(valve, state)

	def readValves(self):
		return self.client.read_coils(0, 16).bits

	def stop(self):
		print 'Disconnecting from Festo...'
		self.client.close()