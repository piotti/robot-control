from milligat import MilligatController
from harvard import HarvardController

from .cfg import CFG

import socket
import traceback
import time
import threading

def get_type(tube_num):
    return CFG['tubes'][str(tube_num)]['type'].lower()
def get_addr(tube_num):
    return CFG['tubes'][str(tube_num)]['ID']


class PumpController:
    def __init__(self, callback):
        self.callback = callback

        self.harvard = HarvardController(callback, ip=CFG["harvard controller ip"], port=int(CFG["harvard controller port"]))
        self.milligat = MilligatController(callback, ip=CFG["milligat controller ip"], port=int(CFG["milligat controller port"]))

        self.t = threading.Thread(target=self.read)
        self.t.start()


    def setFlow(self, tube_num, rate):
        typ = get_type(tube_num)
        addr = get_addr(tube_num)

        if typ == 'harvard':
            self.harvard.setFlow(addr, rate)
        elif typ == 'milligat':
            volume = int(CFG['tubes'][str(tube_num)]['volume'])
            self.milligat.setFlow(addr, rate, volume)
        else:
            print 'Tube type not found, should be harvard or milligat. Check config file.'


    def stopFlow(self, tube_num):
        typ = get_type(tube_num)
        addr = get_addr(tube_num)


        if typ == 'harvard':
            self.harvard.stopFlow(addr)
        elif typ == 'milligat':
            self.milligat.stopFlow(addr)
        else:
            print 'Tube type not found, should be harvard or milligat. Check config file.'

        self.setFlow(addr, 0, 1)
        
    def stop(self):
        self.harvard.close()
        self.milligat.stop()