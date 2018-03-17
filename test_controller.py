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
    update()

class PumpController:
    def __init__(self):
        pass
class ValveController:
    def __init__(self):
        pass

    def readValves(self):
        return [0]*16

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

class BleCharacteristic:
    def __init__(self, uuid, name, typ):
        self.name = name
        self.uuid = uuid
        self.type = typ
        self.char = 0
        self.handle = int(uuid, 16)
        self.has_notify = name=='Temperature' or name=='Pressure'

class Controller:
    def __init__(self):
        self.pump_cbs = []

        self.pumps = None
        self.ble = None
        self.valves = None

        threading.Thread(target=update).start()

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

    def pumps_connect(self):
        self.pumps = PumpController()

    def pumps_disconnect(self):
        pass

    def add_pump_callback(self, cb):
        self.pump_cbs.append(cb)

    ## ROBOT FUNCTIONS ##
    def moveReactor(self, storeNum, bayNum, direction, reactorType = 'normal', between_stores = False, between_bays = False, verbose = None):
        print 'moving reactor'
        print storeNum, bayNum, direction, reactorType, between_stores, between_bays, verbose

    def movePipe(nearNum, farNum, direction, xDisp = .05, yDisp = .03):
        print 'moving pipe'
        print nearNum, farNum, direction, xDisp, yDisp