from ups_lib import INA219
from rtd_lib import tempADC
from pijuice_lib import PiJuice
import os 
import time 
import smbus
bus = smbus.SMBus(1)    # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)

temp_adc = tempADC(bus)
# ina219 = INA219(bus)
pijuice = PiJuice(bus)

# get pressure sensor reading

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
            print(f'channel {i+1}: {temp[i]}')
        time.sleep(1)
        