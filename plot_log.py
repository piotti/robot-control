from Tkinter import *
import Tkinter, Tkconstants, tkFileDialog

import matplotlib.pyplot as plt
 
root = Tk()
root.filename = tkFileDialog.askopenfilename(initialdir = "logs",title = "Select file",filetypes = (("text files","*.txt"),("all files","*.*")))
print (root.filename)

f = open(root.filename)
root.destroy()

ps = {}
ts = {}

for l in f.readlines():
    typ, name, val, time = l.split(' ')
    val = float(val)
    time = float(time)
    if typ == 'P':
        if name in ps:
            ps[name][0].append(time)
            ps[name][1].append(val)
        else:
            ps[name] = [[time], [val]]
    elif typ == 'T':
        if name in ts:
            ts[name][0].append(time)
            ts[name][1].append(val)
        else:
            ts[name] = [[time], [val]]

print ps
print ts 
f, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
for e in sorted(ps.keys()):
    ax1.plot(*ps[e])
for e in sorted(ts.keys()):
    ax2.plot(*ts[e])

ax1.legend(sorted(ps.keys()))
ax1.set_xlabel('Time (s)')
ax1.set_ylabel('Pressure (psi)')

ax2.legend(sorted(ts.keys()))
ax2.set_xlabel('Time (s)')
ax2.set_ylabel('Temp (C)')

plt.show()

