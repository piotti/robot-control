from milligat import MilligatController
from harvard import HarvardController

# from .cfg import CFG

import socket
import traceback
import time
import threading




class PumpController:
    def __init__(self, callback, CFG):
        self.callback = callback
        self.CFG = CFG

        self.harvard = HarvardController(callback, ip=CFG["harvard controller ip"], port=int(CFG["harvard controller port"]))
        self.milligat = MilligatController(callback, ip=CFG["milligat controller ip"], port=int(CFG["milligat controller port"]))


    def setFlow(self, tube_num, rate):
        typ = self.get_type(tube_num)
        addr = self.get_addr(tube_num)

        if typ == 'harvard':
            self.harvard.setFlow(addr, rate)
        elif typ == 'milligat':
            volume = int(self.CFG['tubes'][str(tube_num)]['volume'])
            self.milligat.setFlow(addr, rate, volume)
        else:
            print 'Tube type not found, should be harvard or milligat. Check config file.'

    def get_type(self, tube_num):
        return self.CFG['tubes'][str(tube_num)]['type'].lower()
    def get_addr(self, tube_num):
        return self.CFG['tubes'][str(tube_num)]['ID']


    def stopFlow(self, tube_num):
        typ = self.get_type(tube_num)
        addr = self.get_addr(tube_num)


        if typ == 'harvard':
            self.harvard.stopFlow(addr)
        elif typ == 'milligat':
            self.milligat.stopFlow(addr)
        else:
            print 'Tube type not found, should be harvard or milligat. Check config file.'
        
    def stop(self):
        self.harvard.close()
        self.milligat.stop()