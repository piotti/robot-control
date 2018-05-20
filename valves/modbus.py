import traceback
import time
from pymodbus.client.sync import ModbusTcpClient as ModbusClient


class ValveController:
	def __init__(self, hosts):
		self.hosts = hosts
		print 'connecting to Festos...'
		self.clients = []
		for i in range(len(hosts)):
			self.clients.append(ModbusClient(host=hosts[i]))
			if not self.clients[i].connect():
				print('Couldn\'t connect to host %s' % hosts[i])

		self.closeAll()

	def closeAll(self):
		for i in range(16):
			for client in self.clients:
				client.write_coil(i, False)

	def openAll(self):
		for i in range(16):
			for client in self.clients:
				client.write_coil(i, True)

	def openValve(self, festo, valve):
		self.clients[festo-1].write_coil(valve, True)

	def closeValve(self, festo, valve):
		self.clients[festo-1].write_coil(valve, False)

	def writeValve(self, festo, valve, state):
		self.clients[festo-1].write_coil(valve, state)

	def readValve(self, festo, addr):
		return self.clients[festo-1].read_coils(0, 16).bits[addr]

	def stop(self):
		print 'Disconnecting from Festos...'
		for client in self.clients:
			client.close()