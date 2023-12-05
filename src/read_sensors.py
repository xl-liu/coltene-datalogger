# from i2c_lib.ups_lib import INA219
from i2c_lib.rtd_lib import tempADC
from i2c_lib.pijuice_lib import PiJuice
import os 
import time 
from smbus import SMBus

import sys
sys.path.insert(0, 'adafruit_ads1x15')

import i2c_lib.adafruit_ads1x15.ads1115 as ADS
from i2c_lib.adafruit_ads1x15.analog_in import AnalogIn
from i2c_lib.adafruit_ads1x15.ads1x15 import Mode

bus = SMBus(1)    # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)

temp_adc = tempADC(bus)
# ina219 = INA219(bus)
pijuice = PiJuice(bus)

pres_ads = ADS.ADS1115(bus, gain=2/3)
pres_ads.mode = Mode.CONTINUOUS
pres_chan = AnalogIn(pres_ads, ADS.P0)

# get pressure sensor reading
print('pressure')
print(f'{pres_chan.pressure} mbar')

# get temperature sensor reading
print('temperature')
print(temp_adc.read_all_channels())

# get pijuice status reading
print('battery')
print(pijuice.status.GetChargeLevel())

# read storage space
def get_available_space():
    try:
        stat = os.statvfs('/')  # Replace with the mount point of /dev/root if different
        # Calculate available space
        available_space = stat.f_frsize * stat.f_bavail
        # Convert to human-readable format (bytes to GB)
        available_space_gb = available_space / (1024 ** 3)
        return f"{available_space_gb:.2f}G"
    except Exception as e:
        print(f"Error getting disk space: {e}")
        return "N/A"

print('storage')
print(get_available_space())

# # get waveshare ups status
# bus_voltage = ina219.getBusVoltage_V()             # voltage on V- (load side)
# shunt_voltage = ina219.getShuntVoltage_mV() / 1000 # voltage between V+ and V- across the shunt
# current = ina219.getCurrent_mA()                   # current in mA
# power = ina219.getPower_W()                        # power in W
# p = (bus_voltage - 3)/1.2*100
# if(p > 100):p = 100
# if(p < 0):p = 0

if __name__ == "__main__":
    while True:
        temp = temp_adc.read_all_channels()
        for i in range(temp_adc.n_channels):
            print(f'temperature channel {i+1}: {temp[i]}')
        print(f'pressure: {pres_chan.pressure} mbar')
        print(f'ADC channel 0 voltage: {pres_chan.voltage} V')
        time.sleep(1)
        
