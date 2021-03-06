import nidaqmx

analog_device = 'cDAQ9184-1BD49D8Mod1'
digital_device = 'cDAQ9184-1BD49D8Mod4'

# digital read
left = nidaqmx.Task() 
left.do_channels.add_do_chan(digital_device+'/port0/line0')
# print left.write(True)

right = nidaqmx.Task() 
right.do_channels.add_do_chan(digital_device+'/port0/line1')

p_task = nidaqmx.Task()
p_task.ai_channels.add_ai_voltage_chan(analog_device+"/ai0")


def start():
	left.write(True)
	right.write(True)

def stop():
	left.write(False)
	right.write(False)


def read_pressure():
	raw = p_task.read()
	psi = (raw - 0.5) * 500/3
	return psi


stop()