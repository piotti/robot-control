import socket
import traceback
import time
import threading



class PressureController:
	def __init__(self, callback, ip, port):
		self.ip = ip
		self.port=port
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.s.connect((ip, port))
		except Exception:
			print 'could not connect to alicat'
			return


		self.s.settimeout(2)

		self.running = True


		self.callback = callback
		self.t = threading.Thread(target=self.read)
		self.t.start()


	def read(self):
		while self.running:
			msg=''
			try:
				msg= self.s.recv(32).decode('utf-8')
			except socket.timeout, e:
				err = e.args[0]
				# this next if/else is a bit redundant, but illustrates how the
				# timeout exception is setup
				if err == 'timed out':
					# print 'timeout'
					continue
				else:
					print e
					sys.exit(1)
			except socket.error, e:
					# Something else happened, handle error, exit, etc.
					print e
					exit()
			except Exception:
				try:
					msg = self.s.recv(32)
				except Exception:
					traceback.print_exc()
					exit()

			if msg.strip():
				self.callback(msg)
			time.sleep(2)

	def send_msg(self, msg):
		msg = unicode(msg)
		self.s.sendall(msg)

	def setPressure(self, addr, pressure):
		factor = float(pressure)
		self.send_msg('%sS%d\r' % (addr, int(factor)))

	def zeroPressure(self, addr):
		self.setPressure(addr, 0)
    
	def close(self):
		print 'disconnecting from alicat'
		self.running = False
		self.s.shutdown(1)
		self.s.close()



if __name__ == '__main__':
	def cb(msg):
		print msg,

	c = PressureController(cb, '192.168.1.12', 4003)