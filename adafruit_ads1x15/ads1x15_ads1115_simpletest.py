# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
# import board
# import busio
import ads1115 as ADS
from analog_in import AnalogIn
from ads1x15 import Mode
from smbus import SMBus

# Create the I2C bus
# i2c = busio.I2C(board.SCL, board.SDA)
i2c = SMBus(1)    # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)

# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c)
ads.mode = Mode.CONTINUOUS

# you can specify an I2C adress instead of the default 0x48
# ads = ADS.ADS1115(i2c, address=0x49)

# Create single-ended input on channel 0
chan = AnalogIn(ads, ADS.P0)

# Create differential input between channel 0 and 1
# chan = AnalogIn(ads, ADS.P0, ADS.P1)

print("{:>5}\t{:>5}".format("raw", "v"))

while True:
    print("{:>5}\t{:>5.3f}".format(chan.value, chan.voltage))
    time.sleep(0.5)
