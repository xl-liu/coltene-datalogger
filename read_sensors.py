from ups_lib import INA219
from rtd_lib import tempADC
import pandas as pd

import smbus2 as smbus
bus = smbus.SMBus(1)    # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)

temp_adc = tempADC(bus)
ina219 = INA219(bus)

# start recording 


# get pressure sensor reading

# get temperature sensor reading
temps = temp_adc.read_all_channels()

# write to file


# get battery status
bus_voltage = ina219.getBusVoltage_V()             # voltage on V- (load side)
shunt_voltage = ina219.getShuntVoltage_mV() / 1000 # voltage between V+ and V- across the shunt
current = ina219.getCurrent_mA()                   # current in mA
power = ina219.getPower_W()                        # power in W
p = (bus_voltage - 3)/1.2*100
if(p > 100):p = 100
if(p < 0):p = 0
