import socket
import traceback
import time
import threading



class PressureController:
	def __init__(self, callback, ip, port):
		self.ip = ip
		self.port=port
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.connect((ip, port))
		self.callback = callback
		self.t = threading.Thread(target=self.read)
		self.t.start()


	def read(self):
		while True:
			msg=''
			try:
				msg= self.s.recv(1).decode('utf-8')
			except Exception:
				try:
					msg = self.s.recv(1)
				except Exception:
					traceback.print_exc()
					exit()
			self.callback(msg)
			time.sleep(.25)

	def send_msg(self, msg):
		msg = unicode(msg)
		self.s.sendall(msg)

	def setPressure(self, addr, pressure):
		factor = float(pressure)
		self.send_msg('%sS%d\r' % (addr, int(factor)))

	def zeroPressure(self, addr):
		self.setPressure(addr, 0)
    
	def close(self):
		self.s.shutdown(socket.SHUT_RDWR)
		self.s.close()


if __name__ == '__main__':
	def cb(msg):
		print msg,

	c = PressureController(cb, '192.168.1.12', 4003)