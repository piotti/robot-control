from Tkinter import *
import tkMessageBox as messagebox
import client

DEFAULT_PORT = 'COM19'



class CharacteristicDisplay:

    def __init__(self, master, char, idx, reactor_display):
        self.master = master
        self.char = char
        self.idx = idx
        self.reactor_display = reactor_display

    def display(self):
        self.label = Label(self.master, text=self.char.name)
        self.label.grid(row=self.idx, column=0)

        if self.char.has_notify:
            self.notify_var = IntVar()
            self.notify_button = Checkbutton(self.master, text="Notify", variable=self.notify_var, command=self.notify_cb)
            self.notify_button.grid(row=self.idx, column=4)
        
        self.text_field = Entry(self.master)
        self.text_field.grid(row=self.idx, column=1)

        if self.char.is_writable:
            self.send_button = Button(self.master, text="Send", command=self.send_button_cb)
            self.send_button.grid(row=self.idx, column=2)

        self.read_button = Button(self.master, text="Read", command=self.read_button_cb)
        self.read_button.grid(row=self.idx, column=3)

        # Register a callback for when info is pushed through from device
        self.reactor_display.connection.connection.assign_attrclient_value_callback(self.char.handle+1, self.write_event_cb)

    def notify_cb(self):
        self.reactor_display.connection.connection.characteristic_subscription(self.char.char, False, bool(self.notify_var.get()))

    def read_button_cb(self):
        self.reactor_display.connection.connection.read_by_handle(self.char.handle+1)

    def send_button_cb(self):
        txt = self.text_field.get()
        if self.char.type == 'int':
            txt = hex(int(txt))[2:]
        elif self.char.type == 'text':
            txt = ''.join([hex(ord(e))[2:] for e in txt])
        txt = client.hex_to_string(txt)
        print 'sending', txt
        self.reactor_display.connection.connection.write_by_handle(self.char.handle+1, txt)

    def write_event_cb(self, value):
        value = client.ble_decode(value, msbf=False)
        print 'callback:', value

        if self.char.type == 'int':
            value = int(value, 16)
        elif self.char.type == 'text':
            value = value.decode('hex')

        self.text_field.delete(0,END)
        self.text_field.insert(0,value)


class ReactorDisplay:

    def __init__(self, master, name, dongle):
        self.master = master
        self.name = name
        self.dongle = dongle
        master.minsize(width=400, height=600)
        master.title(name)
        master.protocol("WM_DELETE_WINDOW", self.close_window)

        self.connect_button = Button(master, text="Connect", command=self.connect_button_pressed)
        self.connect_button.grid(row=0, column=0)

        self.connected = False

        self.chars = []

    def close_window(self):
        # Disconnect
        self.disconnect()

        # Destroy
        self.master.destroy()


    def connect_button_pressed(self):
        if not self.connected:
            self.connect()
            self.connected = True
            # Change button to a disconnect button
            self.connect_button["text"] = 'Disconnect'
        else:
            # Disconnect
            self.disconnect()
            self.master.destroy()

    def connect(self):

        # Connect to reactor
        self.connection = self.dongle.connect_to_reactor(self.name)

        # Get characteristics
        chars = self.connection.get_characteristics()

        # Add characteristics to the screen
        for i, char in enumerate(chars):
            # Create new Char display
            cd = CharacteristicDisplay(self.master, char, i+1, self)
            cd.display()

    def disconnect(self):
        if self.connected:
            print 'disconnecting from %s...' % self.name
            self.dongle.disconnect(self.connection.connection)
            self.connected = False

   
class GUI:

    def __init__(self, master):
        self.master = master
        master.title("BLE113 Interface")
        master.minsize(width=400, height=400)
        master.protocol("WM_DELETE_WINDOW", self.close)

        # Dongle Text field and button
        Label(text='Connect to BLE Dongle:').grid(row=0, column=0)
        self.port_field = Entry(master)
        self.port_field.insert(0, DEFAULT_PORT)
        self.port_field.grid(row=1, column=0)
        self.dongle_connect_btn = Button(master, text="Connect to Dongle", command=self.on_dongle_connect_pressed)
        self.dongle_connect_btn.grid(row=1, column=1)

        self.connected = False

        self.rds = []


    # Displays all widgets that show up once connected
    def display_connected_widgets(self):
        # Connect to reactor text field and button
        Label(text='Connect to PSoC:').grid(row=2, column=0)
        self.psoc_var = StringVar(self.master)
        self.psoc_var.set(client.PSOCS.keys()[0]) # default value
        OptionMenu(self.master, self.psoc_var, *client.PSOCS.keys()).grid(row=3, column=0)
        Button(self.master, text='Connect to PSoC', command=self.on_psoc_connect_pressed).grid(row=3, column=1)

        # Terminal
        self.terminal = Text(self.master, height=8, width=30)
        self.terminal.grid(row=4, column=0, columnspan=2)
        self.terminal.config(state=DISABLED)
        sb = Scrollbar(self.master)
        sb.grid(row=4, column=2, sticky=N+S+W)
        sb.config(command=self.terminal.yview)
        self.terminal.config(yscrollcommand=sb.set)

        # Scan button
        Button(self.master, text='Show BLE Scan Results', command=self.on_scan_pressed).grid(row=5, column=0)


    def write_to_terminal(self, text):
        self.terminal.config(state=NORMAL)
        self.terminal.insert(END, '\n'+str(text))
        self.terminal.config(state=DISABLED)
        self.terminal.see(END)


    def on_scan_pressed(self):
        if not self.connected:
            return

        # Scan
        self.write_to_terminal('Scanning...')
        responses = self.dongle.scan_all(timeout=6)
        datas = set([r.get_sender_address() for r in responses])
        for i, d in enumerate(datas):
            decoded = client.ble_decode(d)
            # Check if PSoC in list
            for e in client.PSOCS:
                if client.PSOCS[e] == decoded:
                    decoded = e
                    break
            self.write_to_terminal('\n%d: %s' % (i,  decoded) )


    def on_psoc_connect_pressed(self):
        if not self.connected:
            return

        psoc = self.psoc_var.get()
        self.add_reactor(psoc)

    def on_dongle_connect_pressed(self):
        if self.connected:
            # Disconnect
            self.close()
            return

        # Connect to dongle
        port = self.port_field.get()
        self.dongle = client.Dongle(port)
        self.connected = True

        # Change connect button to disconnect button
        self.dongle_connect_btn['text'] = 'Disconnect'

        self.display_connected_widgets()


    def add_reactor(self, name):

        newWindow = Toplevel(self.master)

        rd = ReactorDisplay(newWindow, name, self.dongle)
        self.rds.append(rd)

    def close(self):
        for rd in self.rds:
            rd.close_window()
        root.destroy()




if __name__ == '__main__':
    root = Tk()
    my_gui = GUI(root)
    root.mainloop()