from Tkinter import *
import tkMessageBox as messagebox

from ble.client import Dongle as BleDongle
from pumps.sock import PumpController 
from valves.modbus import ValveController


class ReactorDisplay:

	def __init__(self, master, idx):
		self.master = master
		self.idx = idx

		# "Reactor: Jaw 1"
		Label(master, text='Reactor\nJaw %d' % idx,
				height=4, width=10, bd=2, relief='ridge').grid(
				row=idx-1, column=0, padx=5, pady=5)

		# "Reactor Type"
		Label(master, text='Reactor  %d' % idx,
				height=4, width=10, bd=2, relief='ridge').grid(
				row=idx-1, column=0, padx=5, pady=5)