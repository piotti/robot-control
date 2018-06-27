from sock import PumpController

from Tkinter import *
import time
import json
from ..threadsafeconsole import ThreadSafeConsole

class GUI:

	def __init__(self, master):
		self.master = master
		master.title("Valves and Pumps")

		# #Read settings from config file
		# d = json.loads(open('config.txt').read())
		# pump_ip=str(d['config']['pumps_ip'])
		# pump_port=int(d['config']['pumps_port'])
		# festo_ip = str(d['config']['festo_ip'])
		# self.VALVE_NAMES = [str(e) for e in d['config']['valve_names']]


		#Add pump controls to GUI
		self.pump_ids=[]
		self.pump_flows=[]
		self.pump_volumes=[]
		for i in range(6):
			#Make Pump Number Label
			Label(master, text='Pump %d:' % (i+1),
				height=1, width=16, anchor=E, justify=RIGHT).grid(
				row=i, column=4, padx=5, pady=5)

			#Make pump address input box
			t = Text(master, height=1, width=4)
			t.grid(row=i, column=5, padx=5, pady=5)
			self.pump_ids.append(t)

			#Make "flow" label
			Label(master, text='Flow:', height=1, 
				width=4, anchor=E, justify=RIGHT).grid(
				row=i, column=6, padx=5, pady=5)

			#Make flow input box
			t = Text(master, height=1, width=4)
			t.grid(row=i, column=7, padx=5, pady=5)
			self.pump_flows.append(t)

			#Make "volume" label
			Label(master, text='Volume:', height=1, width=6,
				anchor=E, justify=RIGHT).grid(
				row=i, column=8, padx=5, pady=5)

			#Make volume input box
			t = Text(master, height=1, width=4)
			t.grid(row=i, column=9, padx=5, pady=5)
			self.pump_volumes.append(t)

		#Make "Echo pumps" button
		Button(master, text='Echo Pumps', height=4,
			command=self.echoPumps).grid(row=6,
			column=4, columnspan=2, rowspan=2, padx=3, pady=5, sticky=E)

		#Make "Send Command" button
		Button(master, text='Send Command\nto Pumps', height=4,
			command=self.sendPumpCommand).grid(row=6,
			column=6, columnspan=2, rowspan=2, padx=3, pady=5)

		#Make "Stop all pumps" button
		Button(master, text='Stop all pumps', height=4,
			command=self.stopAllPumps).grid(row=6,
			column=8, columnspan=2, rowspan=2, padx=3, pady=5, stick=W)

		#Make spacer for right side of GUI
		Label(master, text='').grid(row=0, column=10, padx=20)

		#Make console window
		self.console = ThreadSafeConsole(master, height=4, width=30, bg='light grey')#, state=DISABLED)
		self.console.grid(row=8, column=5, columnspan=4)

		#Connect to pump controller
		self.pump_controller = PumpController(self.printToConsole, ip=pump_ip, port=pump_port)


	def printToConsole(self, msg):
		# self.console.insert(END, msg)
		# self.console.see(END)
		self.console.write(msg)

	#Display version of each pump listed on screen
	def echoPumps(self):
		for pump_id in self.pump_ids:
			addr = pump_id.get("1.0", "end-1c")
			if addr:
				self.pump_controller.checkVer(addr)

	def sendPumpCommand(self):
		#Read inputs in all rows of pump data entry space
		for row in zip(self.pump_ids, self.pump_flows, self.pump_volumes):
			[addr, flow, vol] = [e.get("1.0",'end-1c') for e in row]
			if addr and flow and vol:
				self.pump_controller.setFlow(addr, flow, vol)

	def stopAllPumps(self):
		for pump_id in self.pump_ids:
			addr = pump_id.get("1.0",'end-1c')
			if addr:
				self.pump_controller.setFlow(addr, 0, 1)


	def closeWindow(self):
		self.valve_controller.stop()



if __name__ == '__main__':

	root = Tk()
	gui = GUI(root)

	#Handler for window close
	def on_closing():
		gui.closeWindow()
		root.destroy()
		exit()


	root.protocol("WM_DELETE_WINDOW", on_closing)
	root.mainloop()