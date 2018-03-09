from modbus import ValveController

from Tkinter import *
import time
import json

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

		#Add buttons for valves to GUI
		self.valve_btns=[]
		for i in range(16):
			btn = Button(master, text=self.VALVE_NAMES[i], width=12, height=6, command=self.valvePress(i))
			btn.grid(row=i//4*2, column=i%4, padx=5, pady=5, rowspan=2)
			self.valve_btns.append(btn)

		#Add "Close all Valves" button
		Button(
			master,
			text="Close All Valves",
			height=5,
			width=24,
			command=self.close
		).grid(
			row=8,
			columnspan=2,
			padx=5,
			pady=5
		)


		#Connect to Valve Controller and write valve states to GUI
		self.valve_controller = ValveController(host=festo_ip)
		self.updateValves()


	#Close all valves
	def close(self):
		self.valve_controller.closeAll()
		self.updateValves()

	#Read valve states and update on screen
	def updateValves(self):
		#List of open/closed state of all valves
		#True is open, False is closed
		self.valve_states = self.valve_controller.readValves()
		for i in range(16):
			#Display valve state in GUI
			self.valve_btns[i]['text'] = self.VALVE_NAMES[i] + '\n' + \
			('On' if self.valve_states[i] else 'Off')
			self.valve_btns[i]['bg'] = 'green' if self.valve_states[i] else Button().cget("background")


	#Valve button callback function creator
	def valvePress(self, valve):

		#This function is called when a valve button is clicked
		def valve_func():

			#Toggle valve
			self.valve_controller.writeValve(valve, not self.valve_states[valve])

			#Wait for change to happed and then re-read all valves and update on GUI
			time.sleep(.05)
			self.updateValves()

		return valve_func

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