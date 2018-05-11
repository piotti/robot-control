from configobj import ConfigObj
CFG = ConfigObj('config.ini')
print CFG.keys()
