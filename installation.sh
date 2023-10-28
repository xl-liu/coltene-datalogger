#!/bin/bash

# Update package lists
echo "Upgrading packages..."
sudo apt update
sudo apt upgrade -y

# enable i2c
echo "Enabling i2c"
sudo raspi-config nonint do_i2c 0

# install packages
echo "Installing required packages..."
sudo apt install -y vim i2c-tools git python3-pip

# Install pythan libraries 
sudo mv /usr/lib/python3.11/EXTERNALLY-MANAGED /usr/lib/python3.11/EXTERNALLY-MANAGED/EXTERNALLY-MANAGED.old
sudo pip3 install smbus2 dash numpy flask-bookstrap pandas # flask in included in dash

# clone the repo
git clone https://github.com/xl-liu/coltene-datalogger.git

# move the service file
echo "Creating service file for datalogger"
sudo mv coltene-datalogger/datalogger.service /etc/systemd/system/
sudo systemctl enable datalogger.service 
sudo systemctl start datalogger.service

echo "Creating hotspot"
# change the wifi connection priority
nmcli con modify WuTangLAN connection.id HomeWifi
nmcli con modify HomeWifi connection.autoconnect-priority -10
# create a hotspot
sudo nmcli device wifi hotspot ssid coltene-datalogger password 12345678
nmcli con modify Hotspot connection.autoconnect yes
sudo systemctl restart NetworkManager
