import nidaqmx
import time

analog_device = 'cDAQ9184-1BD49D8Mod1'
digital_device = 'cDAQ9184-1BD49D8Mod4'
ttl_device = 'cDAQ9184-1BD49D8Mod3'

# digital read
left = nidaqmx.Task() 
left.do_channels.add_do_chan(digital_device+'/port0/line0')
# print left.write(True)

right = nidaqmx.Task() 
right.do_channels.add_do_chan(digital_device+'/port0/line1')

p_task = nidaqmx.Task()
p_task.ai_channels.add_ai_voltage_chan(analog_device+"/ai0")

v_task1 = nidaqmx.Task()
v_task2 = nidaqmx.Task()
v_task3 = nidaqmx.Task()
v_task4 = nidaqmx.Task()
v_task5 = nidaqmx.Task()
v_task6 = nidaqmx.Task()
v_task7 = nidaqmx.Task()
v_task8 = nidaqmx.Task()
v_task9 = nidaqmx.Task()
v_task10 = nidaqmx.Task()
v_task11 = nidaqmx.Task()
v_task12 = nidaqmx.Task()
v_task13 = nidaqmx.Task()
v_task14 = nidaqmx.Task()
v_task15 = nidaqmx.Task()


v_task1.do_channels.add_do_chan(ttl_device+'/port0/line0')
v_task2.do_channels.add_do_chan(ttl_device+'/port0/line1')
v_task3.do_channels.add_do_chan(ttl_device+'/port0/line2')
v_task4.do_channels.add_do_chan(ttl_device+'/port0/line3')
v_task5.do_channels.add_do_chan(ttl_device+'/port0/line4')
v_task6.do_channels.add_do_chan(ttl_device+'/port0/line5')
v_task7.do_channels.add_do_chan(ttl_device+'/port0/line6')
v_task8.do_channels.add_do_chan(ttl_device+'/port0/line7')
v_task9.do_channels.add_do_chan(ttl_device+'/port0/line8')
v_task10.do_channels.add_do_chan(ttl_device+'/port0/line9')
v_task11.do_channels.add_do_chan(ttl_device+'/port0/line10')
v_task12.do_channels.add_do_chan(ttl_device+'/port0/line11')
v_task13.do_channels.add_do_chan(ttl_device+'/port0/line12')
v_task14.do_channels.add_do_chan(ttl_device+'/port0/line13')
v_task15.do_channels.add_do_chan(ttl_device+'/port0/line14')


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

def valve_off():
	v_task1.write(True)
	v_task2.write(True)
	v_task3.write(True)
	v_task4.write(True)
	v_task5.write(True)
	v_task6.write(True)
	v_task7.write(True)
	v_task8.write(True)
	v_task9.write(True)
	v_task10.write(True)
	v_task11.write(True)
	v_task12.write(True)
	v_task13.write(True)
	v_task14.write(True)
	v_task15.write(True)
	print 'wash True'

def valve_on():
	v_task1.write(False)
	v_task2.write(False)
	v_task3.write(False)
	v_task4.write(False)
	v_task5.write(False)
	v_task6.write(False)
	v_task7.write(False)
	v_task8.write(False)
	v_task9.write(False)
	v_task10.write(False)
	v_task11.write(False)
	v_task12.write(False)
	v_task13.write(False)
	v_task14.write(False)
	v_task15.write(False)
	print 'wash False'
	
stop()