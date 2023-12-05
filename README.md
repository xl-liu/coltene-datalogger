# coltene-datalogger

## Software ##
1. Flash the Pi </br>
   Tool: [Raspberry Pi Imager] (https://www.raspberrypi.com/software/) or [Etcher] (https://etcher.balena.io/) </br>
   Image: Bookworm. **Raspberry Pi OS Lite (64-bit)** for the Pi Zero 2 W, or **Raspberry Pi OS Lite (32-bit)** for the Pi Zero W
2. Installation </br>
   Refer to *installation.sh*
3. Clone this repo
4. Move *datalogger.service* to `/etc/systemd/system/` on the Pi
5. Program the PiJuice
6. Create a hotspot on the Pi </br>
   a. disable the existing wifi connection </br>
       `command` <br>
   b. create a hotspot interface </br>
       `nmcli dev wifi hotspot ifname wlan0 ssid coltene-datalogger password 12345678` </br>
   c. enable the new hotspot interface </br>
       `command`</br>

## TBC ##

*data_visualization.py* generates a plot from a specified logfile



## Hardware ## 
1. 

