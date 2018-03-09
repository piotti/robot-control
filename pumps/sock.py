import socket
import traceback
import time
import threading



class PumpController:
	def __init__(self, callback, ip='192.168.1.12', port=4001):
		self.ip = ip
		self.port=port
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.s.connect((ip, port))
		except Exception:
			print 'could not connect to pumps'
			return
		self.callback = callback

		self.t = threading.Thread(target=self.read)
		self.t.start()

	def read(self):
		while True:
			msg=''
			try:
				msg= self.s.recv(16).decode('utf-8'),
			except Exception:
				try:
					msg = self.s.recv(16),
				except Exception:
					traceback.print_exc()
					exit()
			self.callback(msg)
			time.sleep(.25)

	def send_msg(self, msg):
		msg = unicode(msg)
		self.s.send(msg)

	def checkVer(self, addr=''):
		addr = str(addr)
		self.send_msg('%sPR VR\r\n' % addr)
	def setAddr(self, addr, current=''):
		self.send_msg('\n%sDN="%s"\r' % (current, str(addr)))
		self.send_msg('\n%sS\r\n' % addr)
	def setParty(self, party):
		self.send_msg('\rPY=%d\r\n' % int(party))
	def setFlow(self, addr, rate, volume):
		try:
			volume = float(volume)
			rate = float(rate)
		except ValueError:
			return
		factor = 256*200*9.8596/float(volume)*float(rate)
		self.send_msg('\n%sSL=%d\r\n' % (addr, int(factor)))
	def stopFlow(self, addr):
		self.setFlow(addr, 0, 1)
	def stop(self):
		self.s.shutdown(socket.SHUT_RDWR)
		self.s.close()