import socket
import traceback
import time
import threading
import argparse
import sys


class RheodyneValveController:
    def __init__(self, callback=lambda x:sys.stdout.write(x + '\n'), 
                ip='192.168.1.12', port=4001):
        self.ip = ip
        self.port=port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('connecting to rheodyne valve @ {} port {}'.format(ip, port))
        try:
            self.s.connect((ip, port))
        except Exception:
            print('could not connect to rheodyne valve @ {} port {}'.format(ip, port))
            return


        self.running = True
        self.s.settimeout(2)


        self.callback = callback

        # self.t = threading.Thread(target=self.read)
        # self.t.start()

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
        print('About to send message to rheodyne valve: {}'.format(msg))
        self.s.send(msg)

    def selector(self, position):
        '''Only for selector valves with 24 ports!!!'''
        if position > 0 and position < 25:
            string = 'P{:02X}\r'.format(int(position))
            self.send_msg(string)
            print('Sent command {} to selector valve'.format(string))
        else:
            print('Error! Invalid position {} specified'.format(position))

    def valve(self, inject):
        '''Only for two-way valves!!!'''
        if inject:
            self.send_msg('V0')
        else:
            self.send_msg('V1')

    def stop(self):
        print 'disconnecting from rheodyne valve'
        self.running = False
        self.s.shutdown(1)
        self.s.close()
        # self.t.join()
        print('disconnected')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Command line interface to control Rheodyne six-port and selector valve via an Arduino')
    parser.add_argument('--ip', help='ip address', default='192.168.1.12')
    parser.add_argument('--port',help='port', type=int, default=4000)
    # selector
    parser.add_argument('-s',dest='selector',help='selector position',type=int)
    group = parser.add_mutually_exclusive_group()
    # six port
    group.add_argument('-inject',action='store_true')
    group.add_argument('-load',action="store_true")
    args = parser.parse_args()

    rheo = RheodyneValveController(
        ip=args.ip,
        port=args.port
    )

    if args.selector:
        rheo.selector(args.selector)

    if args.inject:
        rheo.valve(True)
    elif args.load:
        rheo.valve(False)

    rheo.stop()
