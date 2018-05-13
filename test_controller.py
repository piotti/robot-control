import threading
import time

from cfg import CFG

CHARACTERISTICS = {
    '2a00': {'name': 'Device Name', 'type': 'text'},
    'ab29': {'name': 'Temperature', 'type': 'int'},
    '6a65': {'name': 'Temp Control OnOff', 'type': 'hex'},
    '2784': {'name': 'PID P', 'type': 'hex'},
    'a635': {'name': 'PID I', 'type': 'hex'},
    'a8f2': {'name': 'PID D', 'type': 'hex'},
    '4925': {'name': 'PID Output', 'type': 'int'},
    '25c1': {'name': 'Pressure', 'type': 'int'},
    'b214': {'name': 'Haptic Preset', 'type': 'int'},
    'e947': {'name': 'Haptic Buzz', 'type': 'hex'},
    '1196': {'name': 'Motor Speed', 'type': 'int'},
    'fd69': {'name': 'Stack Address', 'type': 'int'}
}

TEMP_CB = None
PRESSURE_CB = None

import random

def ble_decode(value, msbf=False):
    return hex(value)

def update():
    print 'updating'
    if TEMP_CB:
        TEMP_CB(random.randint(0,5000))
    if PRESSURE_CB:
        PRESSURE_CB(random.randint(0,50))
    time.sleep(1)
    # update()

class PumpController:
    def __init__(self):
        pass
class ValveController:
    def __init__(self):
        pass
    def openValve(self, _):
        pass
    def closeValve(self, _):
        pass

    def readValves(self):
        return [0]*16

class PressureController:
    def __init__(self, callback, ip='192.168.1.12', port=4002):
        self.ip = ip
        self.port=port

    def send_msg(self, msg):
        print 'sending pressure msg:', msg

    def setPressure(self, addr, presure):
        factor = float(pressure)
        print 'setting pressure', addr, presure, factor

    def zeroPressure(self, addr):
        print 'zeroing pressure', addr
    
    def close(self):
        print 'closing pressure controller'

class BleDongle:
    def __init__(self):
        pass
    def connect_to_reactor(self, addr):
        return BleConnection()

class BgConnection:
    def assign_attrclient_value_callback(self, handle, cb):
        print hex(handle)
        if handle == int('ab29', 16) + 1:
            print 'temp handle'
            global TEMP_CB
            TEMP_CB = cb
        elif handle == int('25c1', 16) + 1:
            print 'press handle'
            global PRESSURE_CB
            PRESSURE_CB = cb
    def characteristic_subscription(self, char, b1, b2):
        pass

class BleConnection:
    def __init__(self):
        self.connection = BgConnection()

    def get_characteristics(self):
        chars = {}
        for uuid in CHARACTERISTICS:
            chars[uuid] = BleCharacteristic(uuid, CHARACTERISTICS[uuid]['name'], CHARACTERISTICS[uuid]['type'])
        return chars

    def write(self, *args, **kwargs):
        pass

class BleCharacteristic:
    def __init__(self, uuid, name, typ):
        self.name = name
        self.uuid = uuid
        self.type = typ
        self.char = 0
        self.handle = int(uuid, 16)
        self.has_notify = name=='Temperature' or name=='Pressure'

class Controller:
    def __init__(self, cnsl_print):
        self.cnsl_print = cnsl_print 
        
        self.pump_cbs = []
        self.pressure_cbs = []

        self.pumps = None
        self.ble = None
        self.valves = None
        self.pressure = None

        threading.Thread(target=update).start()


    def pressure_connect(self):
        self.pressure = PressureController(self.pressure_callback, ip=CFG['pressure controller ip'], port=int(CFG['pressure controller port']))

    def pressure_disconnenct(self):
        if self.pressure is not None:
            self.pressure.close()

    def valve_connect(self):
        self.valves = ValveController()

    def valve_disconnect(self):
        pass

    def ble_connect(self):
        self.ble = BleDongle()

    def ble_disconnect(self):
        pass

    # Calls all the callbacks added to the callback list
    def pump_callback(self, msg):
        print 'Pump message received: %s' % msg
        for pcb in self.pump_cbs:
            pcb(msg)


    def pressure_callback(self, msg):
        print 'Pressure message received: %s' % msg
        for pcb in self.pressure_cbs:
            pcb(msg)

    def pumps_connect(self):
        self.pumps = PumpController()

    def pumps_disconnect(self):
        pass

    def add_pump_callback(self, cb):
        self.pump_cbs.append(cb)

    def add_pressure_callback(self, cb):
        self.pressure_cbs.append(cb)

    ## ROBOT FUNCTIONS ##
    def moveReactor(self, storeNum, bayNum, direction, reactorType = 'normal', between_stores = False,
        between_bays = False, verbose = None, callback=lambda x: None):
        print 'moving reactor'
        threading.Thread(target=reactor_finish, args=(callback,)).start()
        print storeNum, bayNum, direction, reactorType, between_stores, between_bays, verbose

    def movePipe(nearNum, farNum, direction, xDisp = .05, yDisp = .03, callback=lambda x: None):
        print 'moving pipe'
        print nearNum, farNum, direction, xDisp, yDisp
        threading.Thread(target=reactor_finish, args=(callback,)).start()


def reactor_finish(cb):
    time.sleep(3)
    cb(0)