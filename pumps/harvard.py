import socket
import traceback
import time
import threading



class HarvardController:
	def __init__(self, callback, ip, port):
		self.ip = ip
		self.port=port
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.connect((ip, port))

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

	def setFlow(self, addr, rate):
		factor = float(rate )

		print 'factor', factor
		print 'msg:', '%sirate %.2f u/m\r' % (addr, factor)
		self.send_msg('\r%sirate %.2f u/m\r' % (addr, factor))
		if factor > 0:
			self.startFlow(addr)

	def stopFlow(self, addr):
		self.send_msg('\r%sstp\r' % (addr))

	def startFlow(self, addr):
		self.send_msg('\r%srun\r' % (addr))

	def close(self):
		print 'disconnecting from harvard'
		self.running = False
		self.s.shutdown(1)
		self.s.close()


if __name__ == '__main__':
	def cb(msg):
		print msg,

	c = HarvardController(cb, '192.168.1.12', 4002)