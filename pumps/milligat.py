import socket
import traceback
import time
import threading



class MilligatController:
	def __init__(self, callback, ip='192.168.1.12', port=4001):
		self.ip = ip
		self.port=port
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print 'connecting to pumps'
		try:
			self.s.connect((ip, port))
		except Exception:
			print 'could not connect to pumps'
			return


		self.running = True
		self.s.settimeout(2)


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
		print 'disconnecting from milligat'
		self.running = False
		self.s.shutdown(1)
		self.s.close()