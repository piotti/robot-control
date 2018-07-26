import time
import sys
#import logging
#import logging.handlers
import sys

#logging.basicConfig(level=logging.INFO, filename='logs.txt')

from bgapi.module import BlueGigaModule, GATTCharacteristic, GATTService, BlueGigaClient, BlueGigaServer, BLEConnection
from bgapi.cmd_def import gap_discoverable_mode, gap_connectable_mode

PORT='COM5'

PSOCS = {
    'PSoC 00392': '00a050e17c5f',
    'PSoC 00795': '00a050a47a8d',
    'PSOC 00759': '00a050a479cb',
	'PSOC 00378': '00a050e1745d',
}

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

def ble_decode(s, msbf=True):
        new = []
        for e in s:
            hx = hex(ord(e))[2:]
            if len(hx) == 1:
                hx = '0'+hx
            new.append(hx)

        if msbf:
            new = new[::-1]
        return ''.join(new)



def hex_to_string(txt):
    if len(txt) == 0:
        txt = '00'
    elif len(txt) == 1:
        txt  = '0'+txt
    assert len(txt) % 2 == 0
    s = ''
    for i in range(0, len(txt), 2):
        num = int(txt[i:i+2], 16)
        s += chr(num)
    return s


class Target:
    def __init__(self, sender):
        self.sender = sender
        self.address_type = 0


class Dongle(BlueGigaClient):
    def __init__(self, port):
        super(Dongle, self).__init__(port=port, baud=115200, timeout=0.1)
        self.port = port
        # BLE Client configuration and start scanning
        self.get_module_info()
        self.reset_ble_state()
        self.delete_bonding()
        self.allow_bonding()

        #self.pipe_logs_to_terminal(level=logging.DEBUG)


        self.connections = {}

    def connect_to_reactor(self, psoc):
        # Scan for psoc
        responses = self.scan_all(timeout=10)
        target = None
        for resp in responses:
            if ble_decode(resp.get_sender_address()) == PSOCS[psoc]:
                print 'found ' + psoc
                target = resp
                break
        else:
            raise Exception("No Advertisements received from psoc")

        # Create new conenction
        connection = self.connect(target=target)
        print 'TARGET PARAMS'
        print repr(target.sender), repr(target.address_type)
        rc = ReactorConnection(connection)

        # Add to table of connections
        self.connections[psoc] = rc

        return rc



class ReactorCharacteristic:
    def __init__(self, ble_char, name, _type):
        self.char = ble_char
        self.name = name
        self.type = _type

        self.has_notify = self.char.has_notify()
        self.has_indicate = self.char.has_indicate()
        self.is_writable = self.char.is_writable()
        self.handle = self.char.handle


class ReactorConnection:
    def __init__(self, ble_connection):
        self.connection = ble_connection

    def get_characteristics(self):
        self.connection.read_by_group_type(group_type=GATTService.PRIMARY_SERVICE_UUID)
        for service in self.connection.get_services():
            print ble_decode(service.uuid)
            service.uuid_formed = ble_decode(service.uuid)
            # print repr(service.uuid)
            self.connection.find_information(service=service)
            self.connection.read_by_type(service=service, type=GATTCharacteristic.CHARACTERISTIC_UUID)
            try:
                self.connection.read_by_type(service=service, type=GATTCharacteristic.CLIENT_CHARACTERISTIC_CONFIG)
            except Exception:
                print 'it didnt have a CCCD'

        rcs = []

        for char in self.connection.get_characteristics():
            uuid = ble_decode(char.uuid)
            if uuid in CHARACTERISTICS:
                rc = ReactorCharacteristic(char, CHARACTERISTICS[uuid]['name'], CHARACTERISTICS[uuid]['type'])
                rcs.append(rc)
            else:
                print uuid

        return rcs


def connect():


    ble_client = BlueGigaClient(port=PORT, baud=115200, timeout=0.1)
    # BLE Client configuration and start scanning
    ble_client.get_module_info()
    ble_client.reset_ble_state()
    ble_client.delete_bonding()
    ble_client.allow_bonding()
    responses = ble_client.scan_all(timeout=2)

    if len(sys.argv)>1 and sys.argv[1] == 'scan':
        devs = {}
        for resp in responses:
            if hasattr(resp, 'data') and resp.data not in devs:
                devs[resp.data] = resp
        for d in devs:
            print d, ':',  devs[d].__dict__
        exit()


    for resp in responses:
        if resp.data == psoc:
            print 'found psoc'
            target = resp
            break
    else:
        raise Exception("No Advertisements received from psoc")
    connection = ble_client.connect(target=target)

    oob_data = "000102030405060708090A0B0C0D0E0F"
    ble_client.set_out_of_band_data(oob_data)
    # connection.request_encryption(bond=True)
    connection.read_by_group_type(group_type=GATTService.PRIMARY_SERVICE_UUID)
    # connection.read_by_group_type(group_type=GATTService.SECONDARY_SERVICE_UUID)

    return ble_client, connection

def get_services(gui, connection):

    for service in connection.get_services():
        print ble_decode(service.uuid)
        service.uuid_formed = ble_decode(service.uuid)
        # print repr(service.uuid)
        connection.find_information(service=service)
        connection.read_by_type(service=service, type=GATTCharacteristic.CHARACTERISTIC_UUID)
        try:
            connection.read_by_type(service=service, type=GATTCharacteristic.CLIENT_CHARACTERISTIC_CONFIG)
        except Exception:
            print 'it didnt have a CCCD'

    for char in connection.get_characteristics():
        uuid = ble_decode(char.uuid)
        if uuid in CHARACTERISTICS:
            print CHARACTERISTICS[uuid]['name']
            CHARACTERISTICS[uuid]['has_notify'] = char.has_notify()
            CHARACTERISTICS[uuid]['has_indicate'] = char.has_indicate()
            CHARACTERISTICS[uuid]['is_writable'] = char.is_writable()
            CHARACTERISTICS[uuid]['handle'] = char.handle
            CHARACTERISTICS[uuid]['obj'] = char
            if gui is not None:
                gui.add_characteristic(uuid, CHARACTERISTICS[uuid])
        else:
            print uuid

    


if __name__ == '__main__':
    connect(None)




