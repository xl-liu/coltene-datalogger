# coltene-datalogger

## Software ##
1. Flash a MicroSD card for the Pi
   - tool: [Raspberry Pi Imager](https://www.raspberrypi.com/software/) or [Etcher](https://etcher.balena.io/) </br>
        *note: in the Rapberry Pi Imager setting, you can enable SSH, and configure the wlan so the pi will automatically connect to the wifi when powered on </br>
   - image: Bookworm. **Raspberry Pi OS Lite (64-bit)** for Pi Zero 2 W, or **Raspberry Pi OS Lite (32-bit)** for Pi Zero W
   
2. Installation
   - boot up the Pi with the SD card </br>
   - clone the repo </br>
        `git clone https://github.com/xl-liu/coltene-datalogger.git` </br>
         `cd coltene-datalogger` </br>
   - run the installation script </br>
        *note: change line 29 in *installation.sh* to match the wlan the pi is connected to `nmcli con modify <ssid> connection.id HomeWifi` </br>
        run `sudo sh installation.sh` </br>
        or if it doesn't work, run the instructions in the file manually </br>
   - reboot the pi
   
3. Program the PiJuice
   - run `pijuice_cli` to bring up the menu </br>
   - go to `IO`, then `IO2`, then `Wakeup`, and choose `RISING EDGE` </br>
   Refer to the [PiJuice git repo](https://github.com/PiSupply/PiJuice/tree/master/Software) for more details

Trouleshooting tips </br>
   - after connecting to the pi's hotspot, you can SSH into the pi via `SSH pi@10.42.0.1`
   - to list the I2C connections, run `i2cdetect -y 1`, you should see `14, 68, ...`
   - to list the existing wlan interfaces, run `nmcli con show`

## Hardware ## 
Componenets:
   - Raspberry Pi Zero 2 W
   - PiJuice Zero with a 3.7V battery
   - Pressure sensor accessories
      - DCDC converter [RNM-0515S](https://recom-power.com/pdf/Econoline/RNM.pdf)
      - ADC [ADS1115 breakout board](https://cdn-learn.adafruit.com/downloads/pdf/adafruit-4-channel-adc-breakouts.pdf)
   - Temperature sensor
   - Misc 
        - USB-A cable to open ends
        - Micro-USB cable to open ends
        - M12 connector set 
        - prototype board

Diagram
